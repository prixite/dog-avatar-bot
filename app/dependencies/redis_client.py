import json
import os
from datetime import timedelta
from dotenv import load_dotenv

import redis


# Load environment variables from .env file
load_dotenv()

REDIS_HOST = os.environ.get('REDIS_HOST')
REDIS_PORT = os.environ.get('REDIS_PORT')



redis_client = redis.Redis(
    host=REDIS_HOST, port=REDIS_PORT, db=0
)



def set_redis_data(key,data):
    redis_client.set(key, json.dumps(data))
    redis_client.expire(key, timedelta(days=1))


def get_hexdata_from_redis(key):
    data = redis_client.get(key)
    if data:
        # str_data = data.decode('utf-8')
        json_data=json.loads(data)              

        cryptocurrencies = []
        symbols_c=""
        # Iterate through the `data` list
        for crypto in json_data['data']:
            # Extract the `name` and `symbol` of each cryptocurrency
            name = crypto['name']
            symbol = crypto['symbol']
            id = str(crypto['id'])
            price = crypto['quote']['USD']['price']  # Extract price

            symbols_c+=symbol+","
            # Append the `name` and `symbol` to the `cryptocurrencies` list as a dictionary
            cryptocurrencies.append({"name": name,"id":id, "symbol": symbol,"price":price})

        return cryptocurrencies
        
    return None


def get_historical_redis_data(key):
    data = redis_client.get(key)
    if data is not None:
        json_data=json.loads(data)
    
        return json_data
    else:
        return None
    


def get_currencylist_redis_data(key):
    data = redis_client.get(key)
    if data is None: 
        # Handle the case where the key does not exist
        return None
    else:
        # Parse the JSON string back into a list
        data = json.loads(data)
        
        # print(data)

        return data
    

def get_list_data(user_message):
    data=get_currencylist_redis_data("curreny_list")

    # Making the user's message lower case for easier comparison
    user_message = user_message.lower()

    # Iterate over the data
    for item in data:
        # Checking if the name or symbol is in the user's message
        if item['name'].lower() in user_message or item['symbol'].lower() in user_message:
            # If either is in the user's message, return the dict
            return item
    
    # If none of the names or symbols is in the user's message, return None
    return None