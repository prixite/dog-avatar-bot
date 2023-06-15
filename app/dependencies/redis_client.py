import json
import os
from datetime import timedelta

import redis
from dotenv import load_dotenv
import logging
# Load environment variables from .env file
load_dotenv()

redis_client = redis.Redis(
    host=os.environ.get("REDIS_HOST"), port=os.environ.get("REDIS_PORT"), db=0
)


def set_redis_data(key, data):
    redis_client.set(key, json.dumps(data))
    redis_client.expire(key, timedelta(days=3))


def get_10k_currency_latest_from_redis(key):
    latest_list_data = redis_client.get(key)
    if latest_list_data:
        latest_list_json_data = json.loads(latest_list_data)

        cryptocurrencies = []
        # Iterate through the `json_data` list
        for data_obj in latest_list_json_data:
            # Extract `data` list
            data_list = data_obj["data"]
            # Iterate through the `data` list
            for crypto in data_list:
                # Extract the `name` and `symbol` of each cryptocurrency
                name = crypto["name"]
                symbol = crypto["symbol"]
                id = str(crypto["id"])
                price = crypto["quote"]["USD"]["price"]  # Extract price

                # Append the `name` and `symbol` to the `cryptocurrencies` list as a dictionary
                cryptocurrencies.append(
                    {"name": name, "id": id, "symbol": symbol, "price": price}
                )

        return cryptocurrencies
    logging.error("latest listing data not found in redis")
    return None


def get_historical_redis_data(key):
    historical_data = redis_client.get(key)
    if historical_data:
        historical_json_data = json.loads(historical_data)
        return historical_json_data
    
    logging.error("Historical Data not found in Redis")
    return None


def get_currencylist_redis_data(key):
    currency_data = redis_client.get(key)
    if currency_data:
        # Parse the JSON string back into a list
        data = json.loads(currency_data)
        return data
    
    # Handle the case where the key does not exist
    return None
