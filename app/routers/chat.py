import datetime
import logging
import pickle
import time

import openai
from fastapi import APIRouter
from langchain.text_splitter import TokenTextSplitter

from app.dependencies.prompts import (
    four_tokens_prompt,
    three_tokens_prompt,
    two_tokens_prompt,
)
from app.dependencies.redis_client import get_historical_redis_data
from app.dependencies.utils import (
    get_each_currency_data,
    get_each_currency_dict_data,
    num_tokens_from_string,
)
from app.internal.chatbot import Chatbot

chatbot = Chatbot()

router = APIRouter()


@router.post("/start_chat")
async def start_chat(user_input):
    current_date = datetime.date.today()
    formatted_date = current_date.strftime("%d %B %Y")
    # data_dict = get_each_currency_dict_data(user_input)
    data_list = get_each_currency_dict_data(user_input)

    if data_list:
        for data_dict in data_list:
            currency_name = data_dict["name"]
            price_coin = data_dict["price"]
            coin_symbol = data_dict["symbol"]

            historical_json_data = get_historical_redis_data("historical_data")

            if historical_json_data:
                extracted_currency_data = get_each_currency_data(
                    historical_json_data, coin_symbol
                )

            else:
                extracted_currency_data = (
                    "PLease Enter Correct Currency name without spaces or symbol!!"
                )
            break

    else:
        currency_name = ""
        price_coin = ""
        coin_symbol = ""
        extracted_currency_data = ""

    num_tokens = num_tokens_from_string(str(extracted_currency_data), "cl100k_base")

    if num_tokens > 3100:
        text_splitter = TokenTextSplitter(chunk_size=3100, chunk_overlap=0)
        texts = text_splitter.split_text(str(extracted_currency_data))
        extracted_currency_data = texts[0]

    future_data = ""

    if coin_symbol:
        try:
            with open(f"app/dependencies/picklefiles/{coin_symbol}.pkl", "rb") as f:
                future_data = pickle.load(f)
        except FileNotFoundError:
            future_data = ""

    docs = chatbot.faiss_index.similarity_search(user_input, k=2)

    # flake8: noqa

    currency_name2 = ""
    currency_name3 = ""
    price_coin2 = ""
    price_coin3 = ""
    currency_name4 = ""
    price_coin4 = ""
    if len(data_list) > 1:
        for i in range(0, len(data_list)):
            if i == 1:
                currency_name2 = data_list[i]["name"]
                price_coin2 = data_list[i]["price"]

            elif i == 2:
                currency_name3 = data_list[i]["name"]
                price_coin3 = data_list[i]["price"]
            elif i == 3:
                currency_name4 = data_list[i]["name"]
                price_coin4 = data_list[i]["price"]

    if len(data_list) == 4:
        messages = four_tokens_prompt(
            docs,
            extracted_currency_data,
            coin_symbol,
            currency_name,
            currency_name2,
            currency_name3,
            currency_name4,
            price_coin,
            price_coin2,
            price_coin3,
            price_coin4,
        )

    elif len(data_list) == 3:
        messages = three_tokens_prompt(
            docs,
            extracted_currency_data,
            coin_symbol,
            currency_name,
            currency_name2,
            currency_name3,
            price_coin,
            price_coin2,
            price_coin3,
        )

    elif len(data_list) == 2:
        messages = two_tokens_prompt(
            docs,
            extracted_currency_data,
            currency_name,
            currency_name2,
            coin_symbol,
            price_coin,
            price_coin2,
        )

    else:
        messages = [
            {
                "role": "system",
                "content": f"""I am going to provide you Historical_currency_price_data in json format that contains information about a crypto currency and its historical data. Also a few Information_hex_pulse documents.\n
                1) The user will ask about the historical price of any currency. You will have that currency information in the Historical_currency_price_data in json format. Use the timestamp in json data to tell the price of a currency of a specific date. \n
                2) If the user asks any question or information that is present or related to the information in the provided documents then answer to that question using only these provided documents.\n
                3) If the user asks some questions that are not related to these documents or you don't find in documents then respond to those question by using your knowledge.\n
                4) Please respond with no salutations and don't refer to the provided documents while answering to user.\n
                5) If the user asks about a date that is ahead of the today's date {formatted_date} or ask about the prediction of price like "will the hex price increase or decrease" then that use the future prices provided to you to predict the price or trend of a currency or price of currency from a future date. \n
                Information_hex_pulse documents Starts:\n {docs}.\n Information_hex_pulse documents End\n
                Historical_currency_price_data of {currency_name} :\n {extracted_currency_data}. \n Historical_currency_price_data of {currency_name} End.\n
                provided future prices of {currency_name}:\n {future_data}\n
                6) The current / today's price or price of currency_name: {currency_name} / currency_symbol: {coin_symbol} on {formatted_date} is {price_coin}. If the user asks about a currency price like "what is xrp price or price of bitcoin", tell the price from the current price of that currency.\n
                """,
            },
        ]

    num_tokens_message = num_tokens_from_string(messages[0]["content"], "cl100k_base")

    if num_tokens_message > 8000:
        text_splitter = TokenTextSplitter(chunk_size=8000, chunk_overlap=0)
        texts = text_splitter.split_text(str(messages[0]["content"]))
        messages[0]["content"] = texts[0]

    messages.append({"role": "user", "content": user_input})

    retry_attempts = 2
    retry_delay = 1  # delay in seconds

    for attempt in range(retry_attempts):
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4", messages=messages, temperature=0
            )
            # if request is successful, break out of loop
            break
        except:
            logging.info("Attempt failed due to openai server")
            if attempt + 1 == retry_attempts:
                return {
                    "role": "system",
                    "content": "Openai server is loaded with requests please try again",
                }
            time.sleep(retry_delay)  # wait before retrying

    message_content = response["choices"][0]["message"]["content"]
    role = response["choices"][0]["message"]["role"]

    response_dict = {"role": role, "content": message_content}
    return response_dict
