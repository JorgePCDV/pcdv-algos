from data_fetcher import fetch_data
from strategy import generate_signal

def backtest():
    df = fetch_data()
    df["signal"] = df.apply(generate_signal, axis=1)

    df["position"] = 0
    df.loc[df["signal"] == "BUY", "position"] = 1
    df.loc[df["signal"] == "SELL", "position"] = 0
    df["position"] = df["position"].ffill()

    df["returns"] = df["Close"].pct_change()
    df["strategy"] = df["returns"] * df["position"]

    final_return = (1 + df["strategy"]).cumprod().iloc[-1]
    print(f"Backtest return: {final_return:.2f}x")

if __name__ == "__main__":
    backtest()
