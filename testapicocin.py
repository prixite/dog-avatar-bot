from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects

url = "https://pro-api.coinmarketcap.com/v3/cryptocurrency/quotes/historical"

# Get the current date and time
time_end = datetime.now()

# Get the date and time one month ago
time_start = time_end - relativedelta(months=1)


parameters = {
    "symbol":"hex",
    "time_start":time_start.strftime("%Y-%m-%dT%H:%M:%SZ"),  # Format the as a string
    "time_end":time_end.strftime("%Y-%m-%dT%H:%M:%SZ"),  
    "aux":"price,volume,market_cap,quote_timestamp",
    "interval":"24h",
    "convert":"USD"
  }

headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': "94440b6c-efe2-410f-8c5e-494392d3605b",
}

session = Session()
session.headers.update(headers)

try:
  response = session.get(url, params=parameters)
  data = json.loads(response.text)
  print(data)

  # Specify the file path where you want to save the data
  file_path = "output.txt"

  # Convert the data to a JSON string
  json_data = json.dumps(data)

  # Write the JSON data to the file
  with open(file_path, "w") as file:
    file.write(json_data)
except (ConnectionError, Timeout, TooManyRedirects) as e:
  print(e)
