import json
import redis
from fastapi import FastAPI
import os
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import openai
import pickle
import pandas as pd
from darts import TimeSeries
from darts.models import RNNModel
from darts.dataprocessing.transformers import Scaler
from darts.utils.missing_values import fill_missing_values
from pandas import Index
from dotenv import dotenv_values
from langchain.document_loaders import PDFMinerLoader
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

config = dotenv_values(".env")

api_keyy = config["key"]
openai.api_key=api_keyy
os.environ["OPENAI_API_KEY"] = api_keyy

app = FastAPI()
# redis_client = redis.Redis(host="localhost", port=6379, db=0)
redis_client = redis.Redis(host="redis", port=6379, db=0)


def load_docs():
    # Define the pickle file path
    pickle_file = "hexpulsedata_pickle.pkl"

    # Check if the pickle file exists
    if os.path.isfile(pickle_file):
        # Load data from the pickle file
        with open(pickle_file, 'rb') as f:
            faiss_index = pickle.load(f)
    else:
        # If pickle file doesn't exist, process the documents and save to a new pickle file
        loader = PDFMinerLoader("hexpulsedata.pdf")
        data = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1400, chunk_overlap=400)
        texts = text_splitter.split_documents(data)
        faiss_index = FAISS.from_documents(texts, OpenAIEmbeddings())
        # Save the faiss index to a pickle file
        with open(pickle_file, 'wb') as f:
            pickle.dump(faiss_index, f)

    return faiss_index


class Chatbot:
    def __init__(self):
        self.faiss_index = load_docs()

def load_hex():

    url = "https://pro-api.coinmarketcap.com/v3/cryptocurrency/quotes/historical"

    # Get the current date and time
    time_end = datetime.now()

    # Get the date and time one month ago
    time_start = time_end - relativedelta(months=1)


    parameters = {
        "symbol":"hex",
        "time_start":time_start.strftime("%Y-%m-%dT%H:%M:%SZ"),  # Format the as a string
        "time_end":time_end.strftime("%Y-%m-%dT%H:%M:%SZ"),  
        "aux":"price,volume,market_cap,quote_timestamp",
        "interval":"24h",
        "convert":"USD"
    }

    headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': "94440b6c-efe2-410f-8c5e-494392d3605b",
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)
    
    return data

chatbot = Chatbot()

def get_redis_key():
    return "hex_data"

def set_redis_data(data):
    key = get_redis_key()
    redis_client.set(key, json.dumps(data))
    redis_client.expire(key, timedelta(days=1))

def get_redis_data():
    key = get_redis_key()
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None

@app.get("/")
async def root():
    return "crypto-api"




@app.post("transcribe_audio")
def transcribe_audio(payload_bytes_data):
    audio_file= payload_bytes_data
    transcript = openai.Audio.transcribe("whisper-1", audio_file)

    return transcript.text



def train_lstm():

    redis_data = get_redis_data()
    if redis_data and "hex_data" in redis_data:
        hex_data = redis_data["hex_data"]
    else:
        return 

    dataa=hex_data['data']['HEX'][0]['quotes']


    # create a list to hold our data
    data_list = []

    for quote in dataa:
        # extract the data we want
        price = quote['quote']['USD']['price']
        volume = quote['quote']['USD']['volume_24h']
        market_cap = quote['quote']['USD']['market_cap']
        quote_timestamp = quote['quote']['USD']['timestamp']
        
        # add to our data list
        data_list.append([ price, volume, market_cap, quote_timestamp])

    # convert list to pandas DataFrame
    df = pd.DataFrame(data_list, columns=['price', 'volume_24h', 'market_cap', 'date'])


    # Prepare your data
    series = TimeSeries.from_dataframe(df, 'date', ['price', 'volume_24h', 'market_cap'])

    # Scale the time series for better performance
    transformer = Scaler()
    series_scaled = transformer.fit_transform(series)

    # Create an RNN model
    model = RNNModel(
        model='LSTM', 
        hidden_dim=20, 
        dropout=0.1, 
        batch_size=4, 
        n_epochs=50, 
        optimizer_kwargs={'lr': 1e-3}, 
        model_name='RNN_Price', 
        random_state=42, 
        training_length=20, 
        input_chunk_length=3, 
        force_reset=True
    )

    # Train the model
    model.fit(series_scaled, verbose=True)
    # Make future predictions (for the next seven days)
    forecast = model.predict(n=7)

    # Rescale the predictions to the original scale
    forecast = transformer.inverse_transform(forecast)


    # convert to pandas DataFrame
    df = forecast.pd_dataframe()

    df_reset = df.reset_index()
    df_reset.columns.name = None
    df_reset = df_reset.reset_index(drop=True)

    
    return df_reset



def load_df_from_redis():
    df_bytes = redis_client.get('future_data')
    if df_bytes is not None:
        # If exists in Redis, de-serialize bytes into DataFrame and return
        df_reset = pickle.loads(df_bytes)
        print("got future")
        return df_reset
    else:
        df=train_lstm()
        # Serialize DataFrame into bytes
        df_bytes = pickle.dumps(df)
        # Store into Redis
        redis_client.set('future_data', df_bytes, ex=86400)
        print("set future")
        return df



@app.post("/start_chat")
async def start_chat(user_input):

    redis_data = get_redis_data()
    if redis_data and "hex_data" in redis_data:
        hex_data = redis_data["hex_data"]
        print("got redis")
    else:
        hex_data = load_hex()
        set_redis_data({"hex_data": hex_data})
        print("set redis")

    future_data=load_df_from_redis()

    # print(future_data)

    docs=chatbot.faiss_index.similarity_search(user_input, k=2)

    messages =[
            {"role": "system", "content":f"""You are a chatbot that have information about Hex, Pulse Chain and PulseX currency.
            I am going to provide you a few information_hex documents and historical hex_data in json format that contains information about  Hex, Pulse Chain and PulseX currency, some FAQ and the historical data. 
            1) Please respond with no salutations and don't refer to the provided documents while answering to user. Never answer like according to the provided documents etc.
            2) If the user asks any question or information that is present or related to the information in the provided documents then answer to that question using only these provided documents. 
            3) I will also provide some documents named as future hex_data. If the user query about the future prices or prediction then respone to that user question by using those future hex data. Always warn the user that predictions can be wrong.
            4) If ther user asks about future predictions then make predictions using only future hex_data.
            4) If the user asks some questions that are not related to these three then response to those question by using your knowledge.\n
            Information_hex documents Start:\n {docs}.\n Information_hex documents End\n
            Historical hex_data Start:\n {hex_data}. \nHistorical hex_data End\n
            Future hex_data Start:\n {future_data}. Future hex_data End \n """},
        ]
    messages.append({"role": "user", "content": user_input})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0
    )

    message_content = response['choices'][0]['message']['content']
    role = response['choices'][0]['message']['role']

    response_dict = {"role": role, "content": message_content}
    return response_dict
