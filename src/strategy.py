def generate_signal(row):
    if row["Close"] > row["ema_20"] and row["rsi_14"] > 55:
        return "BUY"
    elif row["Close"] < row["ema_20"] or row["rsi_14"] < 50:
        return "SELL"
    return "HOLD"
