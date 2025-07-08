# config.py

# === TOGGLE THIS FLAG ===
USE_LIVE = False  # Set to True for live trading

# === Demo Credentials ===
DEMO_API_KEY = "YOUR_DEMO_API_KEY"
DEMO_ACCOUNT_ID = "YOUR_DEMO_ACCOUNT_ID"
DEMO_URL = "https://api-fxpractice.oanda.com"

# === Live Credentials ===
LIVE_API_KEY = "YOUR_LIVE_API_KEY"
LIVE_ACCOUNT_ID = "YOUR_LIVE_ACCOUNT_ID"
LIVE_URL = "https://api-fxtrade.oanda.com"

# === Conditional assignment ===
if USE_LIVE:
    API_KEY = LIVE_API_KEY
    ACCOUNT_ID = LIVE_ACCOUNT_ID
    OANDA_URL = LIVE_URL
else:
    API_KEY = DEMO_API_KEY
    ACCOUNT_ID = DEMO_ACCOUNT_ID
    OANDA_URL = DEMO_URL
