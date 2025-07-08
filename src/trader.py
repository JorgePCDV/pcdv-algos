# trader.py

import oandapyV20
import oandapyV20.endpoints.orders as orders
from config import API_KEY, ACCOUNT_ID

client = oandapyV20.API(access_token=API_KEY)

def place_market_order(units, instrument="EUR_USD"):
    order = {
        "order": {
            "instrument": instrument,
            "units": str(units),
            "type": "MARKET",
            "positionFill": "DEFAULT"
        }
    }
    r = orders.OrderCreate(accountID=ACCOUNT_ID, data=order)
    client.request(r)
    print("✅ Order placed:", r.response)
