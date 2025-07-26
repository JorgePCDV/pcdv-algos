import pandas as pd
from ta.momentum import RSIIndicator
from ta.volatility import BollingerBands

# Load your historical data CSV (must have 'close' prices and a datetime index)
# You can export CSV from OANDA or any data provider
# CSV example columns: time, open, high, low, close, volume
df = pd.read_csv("EURUSD_1H.csv", parse_dates=["time"], index_col="time")

# Calculate indicators
df["rsi"] = RSIIndicator(close=df["close"], window=14).rsi()
bb = BollingerBands(close=df["close"], window=20, window_dev=2)
df["bb_low"] = bb.bollinger_lband()
df["bb_high"] = bb.bollinger_hband()

# Strategy parameters
TP_PIPS = 0.0030
SL_PIPS = 0.0020

# Initialize columns to track trades
df["position"] = 0  # 1 = long, -1 = short, 0 = flat
df["entry_price"] = 0.0
df["exit_price"] = 0.0
df["profit"] = 0.0

in_position = False
position_type = 0
entry_price = 0.0

for i in range(1, len(df)):
    if not in_position:
        # Check entry conditions
        if df["rsi"].iloc[i] < 30 and df["close"].iloc[i] < df["bb_low"].iloc[i]:
            # Enter long
            in_position = True
            position_type = 1
            entry_price = df["close"].iloc[i]
            df.at[df.index[i], "position"] = 1
            df.at[df.index[i], "entry_price"] = entry_price
        elif df["rsi"].iloc[i] > 70 and df["close"].iloc[i] > df["bb_high"].iloc[i]:
            # Enter short
            in_position = True
            position_type = -1
            entry_price = df["close"].iloc[i]
            df.at[df.index[i], "position"] = -1
            df.at[df.index[i], "entry_price"] = entry_price
    else:
        # We are in a trade, check exit conditions (TP or SL hit)
        current_price = df["close"].iloc[i]

        if position_type == 1:
            tp_price = entry_price + TP_PIPS
            sl_price = entry_price - SL_PIPS
            if current_price >= tp_price:
                # Take Profit hit - close position
                df.at[df.index[i], "exit_price"] = tp_price
                df.at[df.index[i], "profit"] = tp_price - entry_price
                in_position = False
                position_type = 0
            elif current_price <= sl_price:
                # Stop Loss hit - close position
                df.at[df.index[i], "exit_price"] = sl_price
                df.at[df.index[i], "profit"] = sl_price - entry_price
                in_position = False
                position_type = 0

        elif position_type == -1:
            tp_price = entry_price - TP_PIPS
            sl_price = entry_price + SL_PIPS
            if current_price <= tp_price:
                df.at[df.index[i], "exit_price"] = tp_price
                df.at[df.index[i], "profit"] = entry_price - tp_price
                in_position = False
                position_type = 0
            elif current_price >= sl_price:
                df.at[df.index[i], "exit_price"] = sl_price
                df.at[df.index[i], "profit"] = entry_price - sl_price
                in_position = False
                position_type = 0

# Calculate total profit in pips
total_profit = df["profit"].sum() * 10000  # multiply by pip factor (1 pip = 0.0001 for EUR/USD)
print(f"Total profit over backtest period: {total_profit:.2f} pips")

# Optional: Save trades to CSV
df.to_csv("backtest_results.csv")

