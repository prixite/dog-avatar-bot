import logging
import pickle
import time

import openai
from fastapi import APIRouter
from langchain.text_splitter import TokenTextSplitter

from app.dependencies.redis_client import get_redis_data, set_redis_data
from app.dependencies.utils import (
    extract_coin_key,
    load_hex,
    num_tokens_from_string,
)
from app.internal.chatbot import Chatbot

chatbot = Chatbot()

router = APIRouter()


@router.post("/start_chat")
async def start_chat(user_input):
    redis_data = get_redis_data()
    if redis_data and "hex_data" in redis_data:
        hex_data = redis_data["hex_data"]
        # print("got redis")
    else:
        # hex_data = load_hex()
        # set_redis_data({"hex_data": hex_data})
        # print("set redis")

        return "Don't have historical data yet in redis"

    new_hex_data = extract_coin_key(user_input, hex_data)

    num_tokens = num_tokens_from_string(str(new_hex_data), "cl100k_base")

    if num_tokens > 3000:
        text_splitter = TokenTextSplitter(chunk_size=3000, chunk_overlap=0)
        texts = text_splitter.split_text(str(new_hex_data))
        new_hex_data = texts[0]

    # new_hex_data = remove_brackets(str(new_hex_data))

    keywords = ["hex", "bitcoin"]
    keywords_second = ["HEX", "BTC"]

    check_user = user_input.lower().split()

    currency_word = ""
    future_data = ""
    currency_word_name = ""

    for word in check_user:
        if word in keywords:
            index = keywords.index(word)
            currency_word = keywords_second[index]
            currency_word_name = word
            break

    if currency_word:
        try:
            with open(f"app/dependencies/{currency_word}.pkl", "rb") as f:
                future_data = pickle.load(f)
        except FileNotFoundError:
            future_data = ""

    # print(f"futureeee data   ====={currency_word_name}",future_data)

    docs = chatbot.faiss_index.similarity_search(user_input, k=2)

    # flake8: noqa
    messages = [
        {
            "role": "system",
            "content": f"""You are a chatbot that have information about crypto currencies and other things too.\n
            I am going to provide you Historical_currency_data in json format that contains information about a crypto currency and the historical data. Also a few Information_hex_pulse documents.\n
            1) The user will ask about the historical price of any currency. You will have that currency information in the Historical_currency_data in json format. Use the timestamp in json data to tell the price of a currency of a specific date. \n
            Make sure to interpret the correct day and month from timestamp. Use that information to tell the price.\n
            2) If the user asks any question or information that is present or related to the information in the provided documents then answer to that question using only these provided documents.\n
            3) If the user query about the price on a date that is present in Future_Data then respone to that user question by using the Future_Data. Always warn the user that predictions can be wrong.\n
            4) If the user asks some questions that are not related to these three then response to those question by using your knowledge.\n
            5) Please respond with no salutations and don't refer to the provided documents while answering to user.\n
            Information_hex_pulse documents Starts:\n {docs}.\n Information_hex_pulse documents End\n
            Historical_currency_data Starts:\n {new_hex_data}. \n Historical_currency_data End.\n
            Future prediction data of {currency_word_name} starts:\n {future_data}\n Future prediction data of {currency_word_name} end.\n
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
