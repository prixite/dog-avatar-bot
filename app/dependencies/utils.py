import json
import os
from datetime import datetime
import openai
import tiktoken
from dateutil.relativedelta import relativedelta
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects


def load_hex():
    url = "https://pro-api.coinmarketcap.com/v3/cryptocurrency/quotes/historical"

    # Get the current date and time
    time_end = datetime.now()

    # Get the date and time one month ago
    time_start = time_end - relativedelta(months=1)


    symbols="""HEX,PLSX,PLS,BTC,ETH,USDT,BNB,USDC,XRP,ADA,DOGE,SOL,MATIC,TRX,LTC,DOT,BUSD,SHIB,AVAX,DAI,WBTC,LINK,LEO,ATOM,UNI,XMR,OKB,ETC,XLM,TON,BCH,ICP,TUSD,FIL,LDO,APT,HBAR,CRO,ARB,VET,NEAR,QNT,GRT,APE,ALGO,USDP,SAND,EOS,RPL,BIT,RNDR,AAVE,EGLD"""



    parameters = {
        "symbol": symbols,
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
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

    # json_data = json.dumps(data)

    return data


def check_spell(user_input):

    messages = [
        {
        "role": "system",
        "content": """You are a chatbot that is restricted to only correcting the spellings of words in a sentence. Don't reply to any user query just correct the spellings of user message. If the sentence has any crypto currency name or token name spelled incorrectly 
        then please correct that too. Please return the same user message to the user after correcting the spellings in it. Don't reply with anything else just return the same whole message to user with correctly spelled words. 
        Don't provide any explanations or answer any query. Here is a list of some correctly spelled crypto currencies names: ["hex","pulsex","pulsechain","bitcoin","ethereum","tether","bnb","usdcoin","xrp",
        "cardano","dogecoin","solana","polygon","tron","litecoin","polkadot","binanceusd","shibainu","avalanche","dai","wrappedbitcoin","chainlink","unussedleo","cosmos","uniswap",
        "monero","okb","ethereumclassic","stellar","toncoin","bitcoincash","internetcomputer","trueusd","filecoin","lidodao","aptos","hedera","cronos","arbitrum","vechain","nearprotocol",
        "quant","thegraph","apeCoin","algorand","paxdollar","thesandbox","eos","rocketpool","bitdao","rendertoken","aave","multiversx"]. Dont add ['s] at the end of any corrected currency name.""",
        },
    ]
    messages.append({"role": "user", "content": user_input})

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages, temperature=0
    )

    message_content = response["choices"][0]["message"]["content"]


    return message_content

def extract_coin_key(user_input, data):
    json_data = json.dumps(data)
    data_string = json_data

    # Define your lists
    first_list = [
        "hex",
        "pulsex",
        "pulsechain",
        "bitcoin",
        "ethereum",
        "tether",
        "bnb",
        "usdcoin",
        "xrp",
        "cardano",
        "dogecoin",
        "solana",
        "polygon",
        "tron",
        "litecoin",
        "polkadot",
        "binanceusd",
        "shibainu",
        "avalanche",
        "dai",
        "wrappedbitcoin",
        "chainlink",
        "unussedleo",
        "cosmos",
        "uniswap",
        "monero",
        "okb",
        "ethereumclassic",
        "stellar",
        "toncoin",
        "bitcoincash",
        "internetcomputer",
        "trueusd",
        "filecoin",
        "lidodao",
        "aptos",
        "hedera",
        "cronos",
        "arbitrum",
        "vechain",
        "nearprotocol",
        "quant",
        "thegraph",
        "apeCoin",
        "algorand",
        "paxdollar",
        "thesandbox",
        "eos",
        "rocketpool",
        "bitdao",
        "rendertoken",
        "aave",
        "multiversx"
    ]
    second_list = [
        "HEX",
        "PLSX",
        "PLS",
        "BTC",
        "ETH",
        "USDT",
        "BNB",
        "USDC",
        "XRP",
        "ADA",
        "DOGE",
        "SOL",
        "MATIC",
        "TRX",
        "LTC",
        "DOT",
        "BUSD",
        "SHIB",
        "AVAX",
        "DAI",
        "WBTC",
        "LINK",
        "LEO",
        "ATOM",
        "UNI",
        "XMR",
        "OKB",
        "ETC",
        "XLM",
        "TON",
        "BCH",
        "ICP",
        "TUSD",
        "FIL",
        "LDO",
        "APT",
        "HBAR",
        "CRO",
        "ARB",
        "VET",
        "NEAR",
        "QNT",
        "GRT",
        "APE",
        "ALGO",
        "USDP",
        "SAND",
        "EOS",
        "RPL",
        "BIT",
        "RNDR",
        "AAVE",
        "EGLD"


    ]

    # Get user input
    user_string = user_input.lower()

    index = 99

    # Check each word in the user string
    for word in user_string.split():
        # print("in loop1")
        if word in first_list:
            # If the word is in the first list, add its index to the new list

            index = first_list.index(word)

    if index != 99:
        # Print the indices
        curreny_symbol = second_list[index]
        # Parse the JSON string into a Python dictionary
        data = json.loads(data_string)

        # Extract the Bitcoin data
        bitcoin_data = data["data"][curreny_symbol]

        # print(bitcoin_data)

        return bitcoin_data
    else:
        user_string=check_spell(user_string)

        user_string=user_string.lower()

        # print(user_string)

        for word in user_string.split():
            # print("in loop = ",word)
            if word in first_list:
                # If the word is in the first list, add its index to the new list
                
                # print("wordssssssssss =",word)

                index = first_list.index(word)

        if index != 99:
            # Print the indices
            curreny_symbol = second_list[index]
            # Parse the JSON string into a Python dictionary
            data = json.loads(data_string)

            # Extract the Bitcoin data
            bitcoin_data = data["data"][curreny_symbol]

            # print(bitcoin_data)


            return bitcoin_data
        else:
            return "I don't Know please enter currency name correctly"


def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


def remove_brackets(input_string):
    input_string = input_string.replace('(', '')
    input_string = input_string.replace(')', '')
    input_string = input_string.replace('[', '')
    input_string = input_string.replace(']', '')
    input_string = input_string.replace('{', '')
    input_string = input_string.replace('}', '')
    
    return input_string