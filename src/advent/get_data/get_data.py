import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go


def get_stock_data(tickers, start, end):
    data = {}

    for ticker in tickers:
        try:
            df = pd.read_csv(f"../CSVs/{ticker}_returns.csv", index_col=0, parse_dates=True)
            data[ticker] = df
        except Exception as e:
            print(f"Error: {e}")

            df = yf.download(ticker, start=start, end=end)
            data[ticker] = df
            df.to_csv(f"../CSVs/{ticker}_returns.csv")

    return data

if __name__ == "__main__":
    tickers = ["AAPL", "GOOG", "MSFT"]
    start = "2023-01-01"
    end = "2024-11-01"

    print("tickers: {}, start: {}, end: {}".format(tickers, start, end))