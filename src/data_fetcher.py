import yfinance as yf
import pandas as pd
import ta

def fetch_data(pair="EURUSD=X", period="30d", interval="1h"):
    df = yf.download(pair, period=period, interval=interval)
    df.dropna(inplace=True)
    df["ema_20"] = ta.trend.ema_indicator(df["Close"], window=20).ema_indicator()
    df["rsi_14"] = ta.momentum.RSIIndicator(df["Close"], window=14).rsi()
    return df
