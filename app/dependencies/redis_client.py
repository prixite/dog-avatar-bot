import json
import os
from datetime import timedelta

import redis
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

redis_client = redis.Redis(
    host=os.environ.get("REDIS_HOST"), port=os.environ.get("REDIS_PORT"), db=0
)


def set_redis_data(key, data):
    redis_client.set(key, json.dumps(data))
    redis_client.expire(key, timedelta(days=1))


def get_10k_latestlist_data_from_redis(key):
    data = redis_client.get(key)
    if data:
        json_data = json.loads(data)

        cryptocurrencies = []
        symbols_c = ""
        # Iterate through the `json_data` list
        for data_obj in json_data:
            # Extract `data` list
            data_list = data_obj["data"]
            # Iterate through the `data` list
            for crypto in data_list:
                # Extract the `name` and `symbol` of each cryptocurrency
                name = crypto["name"]
                symbol = crypto["symbol"]
                id = str(crypto["id"])
                price = crypto["quote"]["USD"]["price"]  # Extract price

                symbols_c += symbol + ","
                # Append the `name` and `symbol` to the `cryptocurrencies` list as a dictionary
                cryptocurrencies.append(
                    {"name": name, "id": id, "symbol": symbol, "price": price}
                )

        return cryptocurrencies

    return None


def get_historical_redis_data(key):
    data = redis_client.get(key)
    if data is not None:
        json_data = json.loads(data)

        return json_data

    return None


def get_currencylist_redis_data(key):
    data = redis_client.get(key)
    if data:
        # Parse the JSON string back into a list
        data = json.loads(data)
        return data

        # Handle the case where the key does not exist
    return None


def get_list_data(user_message):
    data = get_currencylist_redis_data("currency_dict_list")

    user_message = user_message.replace("$", "")
    user_message = user_message.replace("?", "")

    user_message = user_message.lower().split()

    # Add exclusion list
    exclusion_list = ["of", "may", "the", "was", "what", "is"]

    if data:
        for item in data:
            item_name_tokens = item["name"].lower().replace(" ", "").split()
            item_symbol_tokens = item["symbol"].lower().split()

            # Checking if any token from the name or symbol is in the user's message
            for token in item_name_tokens + item_symbol_tokens:
                # Check if token is in the exclusion list
                if token not in exclusion_list and token in user_message:
                    return item

    return None
