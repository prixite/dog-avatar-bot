import json
import logging
import os
import time
from datetime import datetime

import requests
import tiktoken
from dateutil.relativedelta import relativedelta
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

from app.dependencies.redis_client import (
    get_10k_currency_latest_from_redis,
    get_currencylist_redis_data,
    set_redis_data,
)


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def store_10k_currency_latest_in_redis():
    max_attempts = 3
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

    rng = [1, 5001, 10001]
    all_ten_thousand_data = []

    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": os.getenv("COIN_MARKET_CAP_KEY"),
    }

    for i in rng:
        parameters = {"start": i, "limit": 5000, "convert": "USD", "aux": "cmc_rank"}
        attempt_count = 0

        while attempt_count < max_attempts:
            try:
                response = requests.get(url, params=parameters, headers=headers)

                if response.status_code == 200:
                    try:
                        json_data = json.loads(response.text)
                        logging.info(
                            f"Request of value {i} for latest listing data successfull"
                        )
                        all_ten_thousand_data.append(json_data)
                        time.sleep(5)
                        break
                    except json.decoder.JSONDecodeError:
                        logging.error(
                            f"Failed due to parse latest listing api data JSON: {response}"
                        )
                        attempt_count += 1
                else:
                    logging.error(
                        f"Request Failed for latest 10k listing data. Status code: {response}"
                    )
                    attempt_count += 1
            except (ConnectionError, Timeout, TooManyRedirects) as e:
                logging.info(e)
                attempt_count += 1
                time.sleep(
                    3
                )  # Optional: Wait for 2 seconds before next retry to reduce the load on the server

        if attempt_count == max_attempts:
            logging.error("Max attempts reached for latest crypto listing api.")

    set_redis_data("all_10k_listing_data", all_ten_thousand_data)


def store_historical_in_redis():
    store_10k_currency_latest_in_redis()
    currency_ids_list = get_currency_ids()

    if currency_ids_list is None:
        return

    url = "https://pro-api.coinmarketcap.com/v3/cryptocurrency/quotes/historical"

    # Get the current date and time
    time_end = datetime.now()

    # Get the date and time one month ago
    time_start = time_end - relativedelta(months=1)

    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": os.getenv("COIN_MARKET_CAP_KEY"),
    }

    all_data = []
    max_attempts = 3
    count = 0

    for symbols in currency_ids_list:
        # logging.info(count)
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

        session = Session()
        session.headers.update(headers)
        attempt_count = 0

        while attempt_count < max_attempts:
            try:
                response = session.get(url, params=parameters)
                if response.status_code == 200:
                    try:
                        data = json.loads(response.text)
                        all_data.append(data)
                        time.sleep(3)
                        count += 1
                        break
                    except json.decoder.JSONDecodeError:
                        logging.error(
                            f"Historical Json load failed with response: {response}"
                        )
                        attempt_count += 1
                else:
                    logging.error(
                        f"Request Failed for Historical json data with response: {response}"
                    )
                    attempt_count += 1

            except (ConnectionError, Timeout, TooManyRedirects) as e:
                logging.info(e)
                attempt_count += 1
                time.sleep(
                    3
                )  # Optional: Wait for 2 seconds before next retry to reduce the load on the server

        if attempt_count == max_attempts:
            logging.error("Max attempts reached for historical crypto data api.")

    set_redis_data("historical_data", all_data)


def get_currency_ids():
    currency_ids_list = []
    currency_dict_list = []

    cryptocurrencies_10k = get_10k_currency_latest_from_redis("all_10k_listing_data")

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
    if currency_ids_list:
        return currency_ids_list

    return None


def get_each_currency_data(json_data, currency_symbol):
    for data in json_data:
        data = data.get("data", {})
        for _, currency_data in data.items():
            if currency_data["symbol"] == currency_symbol:
                return currency_data

    return None


def get_each_currency_dict_data(user_message):
    list_data_of_currencies = get_currencylist_redis_data("currency_dict_list")

    user_message = user_message.replace("$", "")
    user_message = user_message.replace("?", "")

    user_message = user_message.lower().split()

    # Add exclusion list
    exclusion_list = ["of", "may", "the", "was", "what", "is"]

    matching_currencies = []

    if list_data_of_currencies:
        for item in list_data_of_currencies:
            item_name_tokens = item["name"].lower().replace(" ", "").split()
            item_symbol_tokens = item["symbol"].lower().split()

            # Checking if any token from the name or symbol is in the user's message
            for token in item_name_tokens + item_symbol_tokens:
                # Check if token is in the exclusion list
                if token not in exclusion_list and token in user_message:
                    matching_currencies.append(item)
                    break  # break the inner loop once we found a match in this item

    return matching_currencies
