import logging
import os
import pickle

import pandas as pd
from darts import TimeSeries
from darts.dataprocessing.transformers import Scaler
from darts.models import RNNModel
from rocketry import Rocketry

from app.dependencies.redis_client import get_historical_redis_data
from app.dependencies.utils import (
    get_each_currency_data,
    store_historical_in_redis,
)

app = Rocketry(execution="async", config={"task_execution": "async"})


def train_lstm(currency_name):
    pickle_files_dir = "app/dependencies/picklefiles"

    historical_json_data = get_historical_redis_data("historical_data")

    if historical_json_data is None:
        return

    historical_data = get_each_currency_data(historical_json_data, currency_name)

    try:
        dataa = historical_data["quotes"]
    except Exception:
        return

    # create a list to hold our data
    data_list = []

    for quote in dataa:
        # extract the data we want
        price = quote["quote"]["USD"]["price"]
        volume = quote["quote"]["USD"]["volume_24h"]
        market_cap = quote["quote"]["USD"]["market_cap"]
        quote_timestamp = quote["quote"]["USD"]["timestamp"]

        # add to our data list
        data_list.append([price, volume, market_cap, quote_timestamp])

    # convert list to pandas DataFrame
    df = pd.DataFrame(data_list, columns=["price", "volume_24h", "market_cap", "date"])

    df["date"] = pd.to_datetime(df["date"])

    df["date"] = df["date"].dt.tz_convert(None)

    df.set_index("date", inplace=True)

    df = df.resample("D").mean().reset_index()

    df.fillna(method="ffill", inplace=True)

    # Prepare your data
    series = TimeSeries.from_dataframe(
        df, "date", ["price", "volume_24h", "market_cap"]
    )

    # Scale the time series for better performance
    transformer = Scaler()
    series_scaled = transformer.fit_transform(series)

    # Create an RNN model
    model = RNNModel(
        model="LSTM",
        hidden_dim=20,
        dropout=0.1,
        batch_size=4,
        n_epochs=50,
        optimizer_kwargs={"lr": 1e-3},
        model_name="RNN_Price",
        random_state=42,
        training_length=20,
        input_chunk_length=3,
        force_reset=True,
    )

    # Train the model
    model.fit(series_scaled, verbose=True)
    # Make future predictions (for the next seven days)
    forecast = model.predict(n=7)

    # Rescale the predictions to the original scale
    forecast = transformer.inverse_transform(forecast)

    # convert to pandas DataFrame
    df = forecast.pd_dataframe()

    df_reset = df.reset_index()
    df_reset.columns.name = None
    df_reset = df_reset.reset_index(drop=True)

    # Check if directory exists
    if not os.path.exists(pickle_files_dir):
        # If not, create directory
        os.makedirs(pickle_files_dir)

    try:
        with open(f"{pickle_files_dir}/{currency_name}.pkl", "wb") as f:
            pickle.dump(df_reset, f)
    except PermissionError:
        pass


# daily after 07:00
@app.task("daily after 07:00")
def run_train():
    logging.info("Cron Function Started")
    list_of_currencies = ["HEX", "BTC", "RICHAI", "PLSX", "PLS"]

    store_historical_in_redis()

    try:
        for currency_name in list_of_currencies:
            train_lstm(currency_name)
    except TypeError:
        logging.info("RNN FAILED")
