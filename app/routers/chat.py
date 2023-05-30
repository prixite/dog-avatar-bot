import pickle

import openai
from fastapi import APIRouter

from app.dependencies.redis_client import (
    get_future_data,
    get_redis_data,
    set_future_data,
    set_redis_data,
)
from app.dependencies.rnn import train_lstm
from app.dependencies.utils import extract_coin_key, load_hex
from app.internal.chatbot import Chatbot

chatbot = Chatbot()

router = APIRouter()


@router.post("/start_chat")
async def start_chat(user_input):
    redis_data = get_redis_data()
    if redis_data and "hex_data" in redis_data:
        hex_data = redis_data["hex_data"]
        print("got redis")
    else:
        hex_data = load_hex()
        set_redis_data({"hex_data": hex_data})
        print("set redis")

    new_hex_data = extract_coin_key(user_input, hex_data)

    # print(hex_data)

    # df_bytes = get_future_data()
    # if df_bytes is not None:
    #     future_data = pickle.loads(df_bytes)
    # else:
    #     future_data = train_lstm()
    #     df_bytes = pickle.dumps(future_data)
    #     set_future_data(df_bytes)

    # print(future_data)

    docs = chatbot.faiss_index.similarity_search(user_input, k=2)

    # flake8: noqa
    messages = [
        {
            "role": "system",
            "content": f"""You are a chatbot that have information about Hex, Pulse Chain and PulseX currency.
            I am going to provide you a few information_hex documents and Historical_currency_data in json format that contains information about a crypto currency, some FAQ and the historical data.
            1) If the user asks any question or information that is present or related to the information in the provided documents then answer to that question using only these provided documents.
            2) The user can ask about the historical price of any currency. You will have that currency information in the Historical_currency_data. Use that information to answer.
            3) I will also provide some documents named as future hex_data. If the user query about the future prices or prediction then respone to that user question by using those future hex data. Always warn the user that predictions can be wrong.
            4) If the user asks some questions that are not related to these three then response to those question by using your knowledge.\n
            5) Please respond with no salutations and don't refer to the provided documents while answering to user. Never answer like according to the provided documents etc.
            Information_hex documents Start:\n {docs}.\n Information_hex documents End\n
            Historical_currency_data Start:\n {new_hex_data}. \n Historical_currency_data End\n""",
        },
    ]
    messages.append({"role": "user", "content": user_input})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages, temperature=0
    )

    message_content = response["choices"][0]["message"]["content"]
    role = response["choices"][0]["message"]["role"]

    response_dict = {"role": role, "content": message_content}
    return response_dict
