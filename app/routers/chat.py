import logging
import pickle
import time

import openai
from fastapi import APIRouter
from langchain.text_splitter import TokenTextSplitter

from app.dependencies.redis_client import get_historical_redis_data,get_list_data
from app.dependencies.utils import (
    num_tokens_from_string,
    get_currency_data
)
from app.internal.chatbot import Chatbot

chatbot = Chatbot()

router = APIRouter()


@router.post("/start_chat")
async def start_chat(user_input):

    # store_historical_in_redis()

    data_dict=get_list_data(user_input)

    if data_dict:
        currency_name=data_dict["name"]
        price_coin=data_dict["price"]
        coin_symbol=data_dict["symbol"]

        
        json_data = get_historical_redis_data("historical_data")

        new_hex_data=get_currency_data(json_data,coin_symbol)
    else:
        return "No currrency found"



    # print(f"pp: {currency_name} = ",price_coin)

    num_tokens = num_tokens_from_string(str(new_hex_data), "cl100k_base")

    if num_tokens > 3000:
        text_splitter = TokenTextSplitter(chunk_size=3000, chunk_overlap=0)
        texts = text_splitter.split_text(str(new_hex_data))
        new_hex_data = texts[0]

    # print("new_hex_data = ",new_hex_data)

    # keywords = ["hex", "bitcoin"]
    # keywords_second = ["HEX", "BTC"]

    # check_user = user_input.lower().split()
    # future_data = ""
  

    # if currency_word:
    #     try:
    #         with open(f"app/dependencies/{currency_word}.pkl", "rb") as f:
    #             future_data = pickle.load(f)
    #     except FileNotFoundError:
    #         future_data = ""

    # print(f"futureeee data   ====={currency_word_name}",future_data)

    docs = chatbot.faiss_index.similarity_search(user_input, k=2)

    # flake8: noqa
    messages = [
        {
            "role": "system",
            "content": f"""I am going to provide you Historical_currency_data in json format that contains information about a crypto currency and the historical data. Also a few Information_hex_pulse documents.\n
            1) The user will ask about the historical price of any currency. You will have that currency information in the Historical_currency_data in json format. Use the timestamp in json data to tell the price of a currency of a specific date. \n
            Make sure to interpret the correct day and month from timestamp. Use that information to tell the price.\n
            2) If the user asks about a currency price like "what is xrp price or what is bitcoin price", tell the price from the current price of that currency. The current price or price of {currency_name} is {price_coin}\n
            3) If the user asks any question or information that is present or related to the information in the provided documents then answer to that question using only these provided documents.\n
            4) If the user query about the price on a date that is present in Future_Data then respone to that user question by using the Future_Data. Always warn the user that predictions can be wrong.\n
            5) If the user asks some questions that are not related to these three then response to those question by using your knowledge.\n
            6) Please respond with no salutations and don't refer to the provided documents while answering to user.\n
            Information_hex_pulse documents Starts:\n {docs}.\n Information_hex_pulse documents End\n
            Historical_currency_data of {currency_name} Starts:\n {new_hex_data}. \n Historical_currency_data of {currency_name} End.\n
            """,
        },
    ]
    num_tokens_message = num_tokens_from_string(messages[0]["content"], "cl100k_base")

    if num_tokens_message > 4020:
        text_splitter = TokenTextSplitter(chunk_size=4030, chunk_overlap=0)
        texts = text_splitter.split_text(str(messages[0]["content"]))
        messages[0]["content"] = texts[0]

    messages.append({"role": "user", "content": user_input})

    retry_attempts = 2
    retry_delay = 1  # delay in seconds

    for attempt in range(retry_attempts):
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=messages, temperature=0
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
