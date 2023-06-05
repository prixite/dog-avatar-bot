import tiktoken
import json
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import redis
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging
import os
import time
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from app.dependencies.redis_client import set_redis_data,get_hexdata_from_redis,get_historical_redis_data

def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens





def store_currency_in_redis():
    url="https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

    rng=[1,5001,10001]
    count=1
    for i in rng:
        parameters = {
        "start":i,
        "limit":5000,
        "convert":"USD",
        "aux":"cmc_rank"
        }
    

        headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': os.getenv("COIN_MARKET_CAP_KEY"),
        }

        session = Session()
        session.headers.update(headers)


        try:
            response = session.get(url, params=parameters)
            json_data = json.loads(response.text)

            
            if count==1:
                set_redis_data("first_hexdata",json_data)
            elif count==2:
                set_redis_data("second_hexdata",json_data)
            else:
                set_redis_data("third_hexdata",json_data)

            count+=1
           
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            logging.info(e)






def get_currency_names():

    curreny_ids_list=[]
    curreny_list=[]

    cryptocurrencies_first=get_hexdata_from_redis("first_hexdata")
    cryptocurrencies_second=get_hexdata_from_redis("second_hexdata")
    cryptocurrencies_third=get_hexdata_from_redis("second_hexdata")
    
    
    temp=""
    count=0
    for i in range(0,len(cryptocurrencies_first)):
        

        if count==99:
            temp+=cryptocurrencies_first[i]["id"]
            curreny_ids_list.append(temp)
            count=1
            temp=""
        else:
            temp+=cryptocurrencies_first[i]["id"]+","

        count+=1

        curreny_list.append(cryptocurrencies_first[i])

    temp=""
    count=0
    for i in range(0,len(cryptocurrencies_second)):

        if count==99:
            temp+=cryptocurrencies_second[i]["id"]
            curreny_ids_list.append(temp)
            count=1
            temp=""
        else:
            temp+=cryptocurrencies_second[i]["id"]+","

        count+=1

        curreny_list.append(cryptocurrencies_second[i])

    temp=""
    count=0
    for i in range(0,len(cryptocurrencies_third)):

        if count==99:
            temp+=cryptocurrencies_third[i]["id"]
            curreny_ids_list.append(temp)
            count=1
            temp=""
        else:
            temp+=cryptocurrencies_third[i]["id"]+","

        count+=1

        curreny_list.append(cryptocurrencies_third[i])

    set_redis_data("curreny_list",curreny_list)

    return curreny_ids_list



def store_historical_in_redis():
    store_currency_in_redis()
    curreny_ids_list=get_currency_names()


    url = "https://pro-api.coinmarketcap.com/v3/cryptocurrency/quotes/historical"

    # Get the current date and time
    time_end = datetime.now()

    # Get the date and time one month ago
    time_start = time_end - relativedelta(months=1)

    all_data = []
    count=0
    for symbols in curreny_ids_list:
        parameters = {
            "id":symbols,
            "time_start":time_start.strftime("%Y-%m-%dT%H:%M:%SZ"),  # Format the as a string
            "time_end":time_end.strftime("%Y-%m-%dT%H:%M:%SZ"),  
            "aux":"price,volume,market_cap,quote_timestamp",
            "interval":"24h",
            "convert":"USD"
        }

        headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY':os.getenv("COIN_MARKET_CAP_KEY"),
        }

        session = Session()
        session.headers.update(headers)


        try:
            response = session.get(url, params=parameters)
            data = json.loads(response.text)
            
            print("data = ",count)

            all_data.append(data)

            time.sleep(2)

            count+=1
            
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)

    set_redis_data("historical_data",all_data)





def get_currency_data(json_data, currency_symbol):
    for data in json_data:
        data = data.get('data', {})
        for currency_id, currency_data in data.items():
            if currency_data['symbol'] == currency_symbol:
                return currency_data

    return None

