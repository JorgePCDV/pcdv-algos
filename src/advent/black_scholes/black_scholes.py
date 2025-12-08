import yfinance as yf
import pandas as pd
import numpy as np
from scipy.stats import norm
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# Add Moving Average Cross strat
def add_strategy(data, short_window=20, long_window=50):
    data['Short_MA'] = data['Close'].rolling(window=short_window).mean()
    data['Long_MA'] = data['Close'].rolling(window=long_window).mean()

    data['Signal'] = np.where(
        (data['Short_MA'] > data['Long_MA']) & (data['Short_MA'].shift(1) <= data['Long_MA'].shift(1)), 1,
        np.where(
            (data['Short_MA'] < data['Long_MA']) & (data['Short_MA'].shift(1) >= data['Long_MA'].shift(1)), -1,
            0
        )
    )
    data = data.dropna()
    return data

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

def add_moving_average_strategy(data, short_window=20, long_window=50):
    # Convert Close column to numeric
    data["Close"] = pd.to_numeric(data["Close"], errors="coerce")

    # Drop rows where Close could not be converted
    data = data.dropna(subset=["Close"])

    # Compute moving averages
    data["Short_MA"] = data["Close"].rolling(window=short_window).mean()
    data["Long_MA"] = data["Close"].rolling(window=long_window).mean()

    data = data.dropna()

    # Generate buy/sell/hold signals
    data["Signal"] = np.where(
        (data["Short_MA"] > data["Long_MA"]) & (data["Short_MA"].shift(1) <= data["Long_MA"].shift(1)), 1,
        np.where(
            (data["Short_MA"] < data["Long_MA"]) & (data["Short_MA"].shift(1) >= data["Long_MA"].shift(1)), -1,
            0
        )
    )

    return data

def calculate_indicators(data):
    delta = data["Close"].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data["RSI"] = 100 - (100 / (1 + rs))

    data["MA_20"] = data["Close"].rolling(window=20).mean()
    data["Upper_Band"] = data["MA_20"] + 2 * data["Close"].rolling(window=20).std()
    data["Lower_Band"] = data["MA_20"] - 2 * data["Close"].rolling(window=20).std()

    data = data.dropna()
    return data

def plot(data, ticker):
    fig = go.Figure()

    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        name="Price"
    ))

    fig.update_layout(
        title=f"{ticker} Stock Analysis",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis=dict(rangeslider=dict(visible=False))
    )

    fig.show()


def plot_with_strategy(data, ticker):
    fig = make_subplots(
        rows=3, cols=1, shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=("Candlestick Chart", "RSI", "Volatility")
    )

    # Candlestick chart
    fig.add_trace(go.Candlestick(
        x=data.index, open=data['Open'], high=data['High'],
        low=data['Low'], close=data['Close'], name='Price'
    ), row=1, col=1)

    # Moving averages
    fig.add_trace(go.Scatter(x=data.index, y=data['Short_MA'], mode='lines', name='Short MA'), row=1, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data['Long_MA'], mode='lines', name='Long MA'), row=1, col=1)

    # Strategy
    buy_signals = data[data['Signal'] == 1]
    sell_signals = data[data['Signal'] == -1]

    fig.add_trace(go.Scatter(
        x=buy_signals.index, y=buy_signals['Close'],
        mode='markers', marker=dict(color='green', size=10), name='Buy'
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=sell_signals.index, y=sell_signals['Close'],
        mode='markers', marker=dict(color='red', size=10), name='Sell'
    ), row=1, col=1)

    # RSI
    fig.add_trace(go.Scatter(x=data.index, y=data['RSI'], mode='lines', name='RSI'), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=data.index, y=[70] * len(data), mode='lines',
        line=dict(dash='dash', color='red'), name='Overbought'
    ), row=2, col=1)
    fig.add_trace(go.Scatter(
        x=data.index, y=[30] * len(data), mode='lines',
        line=dict(dash='dash', color='green'), name='Oversold'
    ), row=2, col=1)

    # Volatility
    fig.add_trace(go.Scatter(x=data.index, y=data['Rolling_Std'], mode='lines', name='Rolling Std Dev'), row=3, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data['EWMA_Std'], mode='lines', name='EWMA Std Dev'), row=3, col=1)
    fig.add_trace(go.Scatter(x=data.index, y=data['Annualized_Vol'], mode='lines', name='Annualized Volatility'), row=3, col=1)

    fig.update_layout(
        title=f"{ticker} Stock Analysis",
        xaxis=dict(rangeslider=dict(visible=False)),
        xaxis2_title="Date",
        yaxis1_title="Price",
        yaxis2_title="RSI",
        height=800,
        showlegend=True
    )

    fig.show()


def calculate_volatility(data):
    # Ensure numeric Close column
    data['Close'] = pd.to_numeric(data['Close'], errors='coerce')

    # Drop rows where Close is missing/invalid
    data = data.dropna(subset=["Close"])

    # Compute log returns
    data['log_returns'] = np.log(data['Close'] / data['Close'].shift(1))

    # Drop the first NaN caused by shift(1)
    data = data.dropna(subset=["log_returns"])

    # Rolling volatility (20 days)
    data['Rolling_Std'] = data['log_returns'].rolling(window=20).std()

    # Annualize volatility
    data['Annualized_Vol'] = data['Rolling_Std'] * np.sqrt(252)

    return data

def black_scholes(S, K, T, r, sigma, option_type="call"):
    d1 = ((np.log(S/K)) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    if option_type == "call":
        return S * norm.cdf(d1) - K  * np.exp(-r * T) * norm.cdf(d2)
    elif option_type == "put":
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
    else:
        return "Invalid option type"

def calculate_option_price_bs(data, risk_free_rate=0.03, days_till_expiration=30):
    T = days_till_expiration / 252

    data = data.dropna().copy()

    # call price column
    data.loc[:, "Call_Price"] = data.apply(
        lambda row: black_scholes(
            S=row["Close"],
            K=row["Close"] + 1,
            T=T,
            r=risk_free_rate,
            sigma=row["Annualized_Vol"],
            option_type="call"
        ),
        axis=1
    )

    # put price column
    data.loc[:, "Put_Price"] = data.apply(
        lambda row: black_scholes(
            S=row["Close"],
            K=row["Close"] - 1,
            T=T,
            r=risk_free_rate,
            sigma=row["Annualized_Vol"],
            option_type="put"
        ),
        axis=1
    )

    return data

def plot_with_options(data, ticker):
    fig = make_subplots(
        rows=3,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.02,
        row_heights=[0.6, 0.2, 0.2],
        subplot_titles=["Candlestick chart", "Call premium", "Put premium"]
    )

    fig.add_trace(go.Candlestick(
        x=data.index,
        open=data["Open"],
        high=data["High"],
        low=data["Low"],
        close=data["Close"],
        name="Price"
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data["Call_Price"],
        mode="lines",
        name="Call_Price",
        line=dict(color='green')
    ), row=2, col=1)

    fig.add_trace(go.Scatter(
        x=data.index,
        y=data["Put_Price"],
        mode="lines",
        name="Put_Price",
        line=dict(color='red')
    ), row=3, col=1)

    fig.update_layout(
        title=f"{ticker} Stock Analysis",
        xaxis=dict(rangeslider=dict(visible=False)),
        xaxis3_title="Date",
        yaxis1_title="Price",
        yaxis2_title="Call_Price",
        yaxis3_title="Put_Price",
        height=900,
        showlegend=True
    )

    fig.show()


if __name__ == "__main__":
    tickers = ['AAPL']
    start_date = "2023-01-01"
    end_date = "2023-12-31"

    stock_data = get_stock_data(tickers=tickers, start=start_date, end=end_date)

    for ticker, data in stock_data.items():
        data = calculate_volatility(data)
        data = calculate_option_price_bs(data)
        plot_with_options(data, ticker)