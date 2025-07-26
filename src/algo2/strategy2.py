import pandas as pd
import numpy as np
import datetime
import time
import oandapyV20
import oandapyV20.endpoints.instruments as instruments
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.accounts as accounts

# === CONFIGURATION ===
OANDA_API_KEY = "YOUR_OANDA_API_KEY"
OANDA_ACCOUNT_ID = "YOUR_OANDA_ACCOUNT_ID"
OANDA_ENV = "practice"  # or "live"
INSTRUMENT = "EUR_USD"
GRANULARITY = "H1"
UNITS = 1000  # trade size

client = oandapyV20.API(access_token=OANDA_API_KEY)

# === INDICATOR CALCULATION ===
def calculate_indicators(df):
    df['ma20'] = df['close'].rolling(window=20).mean()
    df['stddev'] = df['close'].rolling(window=20).std()
    df['upper_bb'] = df['ma20'] + (2 * df['stddev'])
    df['lower_bb'] = df['ma20'] - (2 * df['stddev'])

    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    tr = pd.concat([
        df['high'] - df['low'],
        abs(df['high'] - df['close'].shift()),
        abs(df['low'] - df['close'].shift())
    ], axis=1).max(axis=1)
    df['atr'] = tr.rolling(window=14).mean()
    return df

# === FETCH HISTORICAL DATA ===
def get_candles():
    params = {"granularity": GRANULARITY, "count": 200, "price": "M"}
    r = instruments.InstrumentsCandles(instrument=INSTRUMENT, params=params)
    client.request(r)
    candles = r.response["candles"]
    records = [{
        "time": c["time"],
        "open": float(c["mid"]["o"]),
        "high": float(c["mid"]["h"]),
        "low": float(c["mid"]["l"]),
        "close": float(c["mid"]["c"]),
        "volume": c["volume"]
    } for c in candles if c["complete"]]
    df = pd.DataFrame(records)
    df["time"] = pd.to_datetime(df["time"])
    df.set_index("time", inplace=True)
    return calculate_indicators(df)

# === SIGNAL GENERATION ===
def generate_signal(df):
    last = df.iloc[-1]
    if last['close'] < last['lower_bb'] and last['rsi'] < 30:
        return "buy", last['atr']
    elif last['close'] > last['upper_bb'] and last['rsi'] > 70:
        return "sell", last['atr']
    return None, None

# === PLACE ORDER ===
def place_order(signal, atr):
    stop_loss_pips = round(1.5 * atr, 5)
    price = get_latest_price()
    sl_price = None
    tp_price = None
    units = UNITS if signal == "buy" else -UNITS

    if signal == "buy":
        sl_price = round(price - stop_loss_pips, 5)
        tp_price = round(price + (price - sl_price), 5)
    else:
        sl_price = round(price + stop_loss_pips, 5)
        tp_price = round(price - (sl_price - price), 5)

    data = {
        "order": {
            "instrument": INSTRUMENT,
            "units": str(units),
            "type": "MARKET",
            "positionFill": "DEFAULT",
            "stopLossOnFill": {"price": str(sl_price)},
            "takeProfitOnFill": {"price": str(tp_price)},
        }
    }
    r = orders.OrderCreate(accountID=OANDA_ACCOUNT_ID, data=data)
    client.request(r)
    print(f"Trade executed: {signal.upper()} | Entry: {price} | SL: {sl_price} | TP: {tp_price}")

def get_latest_price():
    r = instruments.InstrumentsCandles(instrument=INSTRUMENT, params={"granularity": GRANULARITY, "count": 1})
    client.request(r)
    c = r.response["candles"][-1]
    return float(c["mid"]["c"])

def wait_until_next_hour():
    """Sleep until the start of the next full UTC hour."""
    now = datetime.datetime.utcnow()
    next_hour = (now + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    sleep_seconds = (next_hour - now).total_seconds()
    print(f"Sleeping for {int(sleep_seconds)} seconds until next hour...")
    time.sleep(sleep_seconds)

def run_strategy():
    while True:
        now = datetime.datetime.utcnow()
        print(f"[{now}] Running strategy...")

        try:
            df = get_candles()
            signal, atr = generate_signal(df)
            if signal:
                print(f"Signal: {signal.upper()} | ATR: {atr}")
                place_order(signal, atr)
            else:
                print("No trade signal.")
        except Exception as e:
            print(f"Error: {e}")

        # Sleep until next full hour
        wait_until_next_hour()

if __name__ == "__main__":
    run_strategy()
