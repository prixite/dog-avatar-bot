import json
import redis
from datetime import timedelta
from fastapi import FastAPI
import os
import openai
from langchain.document_loaders import PDFMinerLoader
from langchain.vectorstores import FAISS
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter

os.environ["OPENAI_API_KEY"] = "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"

app = FastAPI()
# redis_client = redis.Redis(host="localhost", port=6379, db=0)
redis_client = redis.Redis(host="redis", port=6379, db=0)


def load_docs():
    loader = PDFMinerLoader("hexdata.pdf")
    data = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1400, chunk_overlap=400)
    texts = text_splitter.split_documents(data)
    faiss_index = FAISS.from_documents(texts, OpenAIEmbeddings())
    return faiss_index

class Chatbot:
    def __init__(self):
        self.faiss_index = load_docs()

def load_hex():
    with open("hexcoin.txt", "r") as file:
        data = file.read()
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
    if redis_data and "docs" in redis_data:
        hex_data = redis_data["docs"]
    else:
        hex_data = load_hex()
        set_redis_data({"docs": hex_data})


    docs=chatbot.faiss_index.similarity_search(user_input, k=2)

    messages =[
            {"role": "system", "content":f"""You are a chatbot that is restricted to hex currency and can answer questions only related to Hex Crypto currency. I am going to provide you a few documents and historical hex coin data that contains information about hex, some FAQ and the historical hex data. If the user asks any question or information that is present or 
            related to the information in the provided documents then answer to that question, provide information or generate an answer to user using only these documents, don't answer from your own. 
            Provided Documents Start: {docs}.\n Provided Documents End.
            Historical Data for HEX Start: {hex_data}. \nHistorical Data for HEX End

            If the conversation is not related to hex coin try to bring back 
            conversation to hex coin related information only. """},
        ]
    messages.append({"role": "user", "content": user_input})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
    )

    message_content = response['choices'][0]['message']['content']
    role = response['choices'][0]['message']['role']

    response_dict = {"role": role, "content": message_content}
    return response_dict
