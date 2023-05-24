import json
import os
from datetime import datetime

from dateutil.relativedelta import relativedelta
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects


def load_hex():
    url = "https://pro-api.coinmarketcap.com/v3/cryptocurrency/quotes/historical"

    # Get the current date and time
    time_end = datetime.now()

    # Get the date and time one month ago
    time_start = time_end - relativedelta(months=1)

    parameters = {
        "symbol": "hex",
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

    return data
