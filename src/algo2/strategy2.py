import time
import datetime
import oandapyV20
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.instruments as instruments
import pandas as pd
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

# === CONFIG ===
API_KEY_PRACTICE = "YOUR_OANDA_PRACTICE_API_KEY"
API_KEY_LIVE = "YOUR_OANDA_LIVE_API_KEY"
ACCOUNT_ID_PRACTICE = "YOUR_PRACTICE_ACCOUNT_ID"
ACCOUNT_ID_LIVE = "YOUR_LIVE_ACCOUNT_ID"
USE_PAPER = True  # Set False for live trading

INSTRUMENT = "EUR_USD"
UNITS = 1000
TP_PIPS = 0.0030  # 30 pips
SL_PIPS = 0.0020  # 20 pips

ACCOUNT_ID = ACCOUNT_ID_PRACTICE if USE_PAPER else ACCOUNT_ID_LIVE
API_KEY = API_KEY_PRACTICE if USE_PAPER else API_KEY_LIVE
client = oandapyV20.API(access_token=API_KEY)

def fetch_candles():
    params = {"granularity": "H1", "count": 100, "price": "M"}
    r = instruments.InstrumentsCandles(instrument=INSTRUMENT, params=params)
    client.request(r)
    candles = r.response["candles"]
    prices = [float(c["mid"]["c"]) for c in candles]
    df = pd.DataFrame(prices, columns=["close"])
    return df

def get_signal():
    df = fetch_candles()
    rsi = RSIIndicator(close=df["close"], window=14).rsi()
    bb = BollingerBands(close=df["close"], window=20, window_dev=2)
    last_rsi = rsi.iloc[-1]
    last_price = df["close"].iloc[-1]
    lower_bb = bb.bollinger_lband().iloc[-1]
    upper_bb = bb.bollinger_hband().iloc[-1]

    print(f"RSI: {last_rsi:.2f} | Price: {last_price:.5f} | BB Low: {lower_bb:.5f} | BB High: {upper_bb:.5f}")

    if last_rsi < 30 and last_price < lower_bb:
        return "buy", last_price
    elif last_rsi > 70 and last_price > upper_bb:
        return "sell", last_price
    return None, None

def place_order(signal, price):
    sl = price - SL_PIPS if signal == "buy" else price + SL_PIPS
    tp = price + TP_PIPS if signal == "buy" else price - TP_PIPS
    units = UNITS if signal == "buy" else -UNITS

    order_data = {
        "order": {
            "instrument": INSTRUMENT,
            "units": str(units),
            "type": "MARKET",
            "positionFill": "DEFAULT",
            "stopLossOnFill": {"price": f"{sl:.5f}"},
            "takeProfitOnFill": {"price": f"{tp:.5f}"}
        }
    }

    r = orders.OrderCreate(accountID=ACCOUNT_ID, data=order_data)
    client.request(r)
    print(f"{signal.upper()} order placed at {price:.5f}, SL={sl:.5f}, TP={tp:.5f}")

def wait_until_next_hour():
    now = datetime.datetime.utcnow()
    next_hour = (now + datetime.timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    sleep_seconds = (next_hour - now).total_seconds()
    print(f"Sleeping {int(sleep_seconds)} seconds until next full hour...")
    time.sleep(sleep_seconds)

def run_strategy():
    last_candle_time = None

    while True:
        try:
            df = fetch_candles()
            latest_candle_time = df.index[-1] if hasattr(df.index, "__len__") else None
            latest_candle_time = df.index[-1].replace(minute=0, second=0, microsecond=0) if hasattr(df.index, "__len__") else None

            # If index not datetime, fallback to UTC now hour:
            if latest_candle_time is None or not isinstance(latest_candle_time, pd.Timestamp):
                latest_candle_time = datetime.datetime.utcnow().replace(minute=0, second=0, microsecond=0)

            if last_candle_time is None:
                last_candle_time = latest_candle_time
                print(f"[{datetime.datetime.utcnow()} UTC] Starting fresh at candle {last_candle_time}")
            elif latest_candle_time > last_candle_time:
                print(f"[{datetime.datetime.utcnow()} UTC] New candle detected: {latest_candle_time}")
                signal, price = get_signal()
                if signal:
                    place_order(signal, price)
                else:
                    print("No trade signal.")
                last_candle_time = latest_candle_time
            else:
                print(f"[{datetime.datetime.utcnow()} UTC] No new candle yet (last: {last_candle_time})")

        except Exception as e:
            print(f"Error: {e}")

        time.sleep(60)  # check every minute

if __name__ == "__main__":
    run_strategy()
