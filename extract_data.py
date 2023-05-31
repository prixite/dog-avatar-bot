import openai
import os

openai.api_key
os.environ["OPENAI_API_KEY"]


def check_spell(user_input):
    messages = [
        {
            "role": "system",
            "content": """You are a chatbot that is restricted to only correcting the spellings of words in a sentence. If the sentence has any crypto currency name or token name spelled incorrectly
        then please correct that too. Please return the same user message to the user after correcting the spellings in it. Don't reply with anything else just return the same whole message to user with correctly spelled words.
        Don't provide any explanations or answer any query. Here is a list of some correctly spelled crypto currencies names: ["hex","pulsex","pulsechain","bitcoin","ethereum","tether","bnb","usdcoin","xrp",
        "cardano","dogecoin","solana","polygon","tron","litecoin","polkadot","binanceusd","shibainu","avalanche","dai","wrappedbitcoin","chainlink","unussedleo"]. Dont add ['s] at the end of any corrected currency name.""",
        },
    ]
    messages.append({"role": "user", "content": user_input})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages, temperature=0
    )

    message_content = response["choices"][0]["message"]["content"]

    return message_content


while True:
    inp = input("User: ")
    print(check_spell(inp))
