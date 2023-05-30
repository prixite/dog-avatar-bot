import json
import os
from datetime import datetime
import pickle
from dateutil.relativedelta import relativedelta
from requests import Session
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import FAISS
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import openai

openai.api_key = "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"

os.environ["OPENAI_API_KEY"]="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"

def load_hex():
    url = "https://pro-api.coinmarketcap.com/v3/cryptocurrency/quotes/historical"

    # Get the current date and time
    time_end = datetime.now()

    # Get the date and time one month ago
    time_start = time_end - relativedelta(months=1)

    parameters = {
        "symbol":"HEX,BTC,ETH,USDT,BNB,USDC,XRP,ADA,DOGE,SOL,MATIC",
        "time_start": time_start.strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),  # Format the as a string
        "time_end": time_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "aux": "price,volume,market_cap,quote_timestamp",
        "interval": "24h",
        "convert": "USD",
    }

    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": os.getenv("COIN_MARKET_CAP_KEY"),
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(url, params=parameters)
        data = json.loads(response.text)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

    json_data = json.dumps(data)

    return json_data



def extract_coin_key(user_input,json_data):
    data_string=json_data

   # Define your lists
    first_list = ['hex', 'bitcoin', 'ethereum', 'tether', 'bnb', 'usdcoin', 'xrp', 'cardano', 'dogecoin', 'solana', 'polygon']
    second_list = ['HEX', 'BTC', 'ETH', 'USDT', 'BNB', 'USDC', 'XRP', 'ADA', 'DOGE', 'SOL', 'MATIC']

    # Get user input
    user_string = user_input.lower()


    index=99
    # Check each word in the user string
    for word in user_string.split():
        if word in first_list:
            # If the word is in the first list, add its index to the new list

            index=first_list.index(word)

    if index!=99:
        # Print the indices
        curreny_symbol=second_list[index]
        # Parse the JSON string into a Python dictionary
        data = json.loads(data_string)

        # Extract the Bitcoin data
        bitcoin_data = data['data'][curreny_symbol]

        # print(bitcoin_data)

        return bitcoin_data
    else:
        return "I don't Know please enter currency name correctly"
