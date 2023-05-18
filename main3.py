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
from dotenv import dotenv_values
from langchain.document_loaders import PDFMinerLoader
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

config = dotenv_values(".env")

api_key = config["key"]

os.environ["OPENAI_API_KEY"] = api_key

app = FastAPI()
# redis_client = redis.Redis(host="localhost", port=6379, db=0)
redis_client = redis.Redis(host="redis", port=6379, db=0)


def load_docs():
    loader = PDFMinerLoader("hexpulsedata.pdf")
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1400, chunk_overlap=400)
    texts = text_splitter.split_documents(data)
    faiss_index = FAISS.from_documents(texts, OpenAIEmbeddings())
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

@app.post("/start_chat")
async def start_chat(user_input):

    redis_data = get_redis_data()
    if redis_data and "hex_data" in redis_data:
        hex_data = redis_data["hex_data"]
        # print("got redis")
    else:
        hex_data = load_hex()
        set_redis_data({"hex_data": hex_data})
        # print("set redis")

    docs=chatbot.faiss_index.similarity_search(user_input, k=2)

    messages =[
            {"role": "system", "content":f"""You are a chatbot that is restricted to hex currency and can answer questions only related to Hex Crypto currency. 
            I am going to provide you a few documents and historical hex coin data in json format that contains information about hex, some FAQ and the historical hex currency data. Respond with no salutations.
            If the user asks any question or information that is present or 
            related to the information in the provided documents then answer to that question using only these provided documents, don't answer from your own.
            Provided Documents Start: {docs}.\n Provided Documents End.
            Historical Data for HEX Start: {hex_data}. \nHistorical Data for HEX End

            If the conversation is not related to hex, pulse chain and pulseX try to bring back 
            conversation to hex, pulse chain and pulseX related information only. """},
        ]
    messages.append({"role": "user", "content": user_input})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.1
    )

    message_content = response['choices'][0]['message']['content']
    role = response['choices'][0]['message']['role']

    response_dict = {"role": role, "content": message_content}
    return response_dict
