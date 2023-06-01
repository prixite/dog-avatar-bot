import pandas as pd
from darts import TimeSeries
from darts.dataprocessing.transformers import Scaler
from darts.models import RNNModel
import pickle
from app.dependencies.redis_client import get_redis_data
from rocketry.conds import daily
from rocketry import Rocketry

app = Rocketry(execution="async", config={"task_execution": "async"})


def train_lstm(currency_name):
    redis_data = get_redis_data()
    if redis_data and "hex_data" in redis_data:
        hex_data = redis_data["hex_data"]
    else:
        return

    # print(f"hexdataaaaaaaaaaaaaaaaaaaaaaaaa {currency_name} ===========",hex_data)

    dataa = hex_data["data"][currency_name][0]["quotes"]

    # print("dataaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa=========== ",dataa)

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

    # print("dataframefdarnme    data frame   ====================",df)

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

    # Save the DataFrame to a pickle file
    with open(f"app/dependencies/{currency_name}.pkl", "wb") as f:
        pickle.dump(df_reset, f)

    # print(f"HAhhhhhhhhhhhhhhhhhhhhhhh Stoppppppppppp me I am runninggggggggggggggggggg= {currency_name}")


@app.task(daily)
def run_train():
    list_c = ["HEX", "BTC"]

    for c in list_c:
        train_lstm(c)
