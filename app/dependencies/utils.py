import json
import logging
import os
import time
from datetime import datetime

import tiktoken
from dateutil.relativedelta import relativedelta
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

from app.dependencies.redis_client import (
    get_10k_latestlist_data_from_redis,
    set_redis_data,
)

# os.getenv("COIN_MARKET_CAP_KEY")


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def store_10k_currency_latest_in_redis():
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

    rng = [1, 5001, 10001]
    all_ten_thousand_data = []
    for i in rng:
        parameters = {"start": i, "limit": 5000, "convert": "USD", "aux": "cmc_rank"}

        headers = {
            "Accepts": "application/json",
            "X-CMC_PRO_API_KEY": os.getenv("COIN_MARKET_CAP_KEY"),
        }

        session = Session()
        session.headers.update(headers)

        try:
            response = session.get(url, params=parameters)
            json_data = json.loads(response.text)

            all_ten_thousand_data.append(json_data)

        except (ConnectionError, Timeout, TooManyRedirects) as e:
            logging.info(e)

    set_redis_data("all_10k_listing_data", all_ten_thousand_data)


def get_currency_ids():
    currency_ids_list = []
    currency_dict_list = []

    cryptocurrencies_10k = get_10k_latestlist_data_from_redis("all_10k_listing_data")

    temp_100_strings = ""
    count = 0
    for i in range(0, len(cryptocurrencies_10k)):
        if count == 99:
            temp_100_strings += cryptocurrencies_10k[i]["id"]
            currency_ids_list.append(temp_100_strings)
            count = 0
            temp_100_strings = ""
        else:
            temp_100_strings += cryptocurrencies_10k[i]["id"] + ","

        count += 1

        currency_dict_list.append(cryptocurrencies_10k[i])

    set_redis_data("currency_dict_list", currency_dict_list)

    return currency_ids_list


def store_historical_in_redis():
    store_10k_currency_latest_in_redis()
    currency_ids_list = get_currency_ids()

    url = "https://pro-api.coinmarketcap.com/v3/cryptocurrency/quotes/historical"

    # Get the current date and time
    time_end = datetime.now()

    # Get the date and time one month ago
    time_start = time_end - relativedelta(months=1)

    all_data = []
    count = 0
    for symbols in currency_ids_list:
        parameters = {
            "id": symbols,
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

            logging.info(count)

            all_data.append(data)

            time.sleep(2)

            count += 1

        except (ConnectionError, Timeout, TooManyRedirects) as e:
            logging.info(e)

    set_redis_data("historical_data", all_data)


def get_currency_data(json_data, currency_symbol):
    for data in json_data:
        data = data.get("data", {})
        for _, currency_data in data.items():
            if currency_data["symbol"] == currency_symbol:
                return currency_data

    return None
