import os
import sys
from time import sleep

from binance import ThreadedWebsocketManager
from binance.client import Client

from utils import get_valid_buy_quantity, get_valid_sell_quantity

# ========================
# Setup
# ========================
api_key = os.environ.get("binance_api")
api_secret = os.environ.get("binance_secret")
client = Client(api_key, api_secret)

# ========================
# Query account information
# ========================
print(client.get_account())
print(client.get_asset_balance(asset="BTC")["free"])

# ========================
# Initialize socket manager
# ========================
def handle_socket_message(msg):
    print(f"message type: {msg['e']}")
    print(msg)


twm = ThreadedWebsocketManager()
twm.start()

# ========================
# Querying current prices
# ========================
# API call
print(client.get_symbol_ticker(symbol="BTCUSDT")["price"])

# Websocket
btc_ticker = twm.start_symbol_ticker_socket(
    callback=handle_socket_message, symbol="BTCUSDT"
)
sleep(4)
twm.stop_socket(btc_ticker)

# ========================
# Query historical prices
# ========================
# API call
klines = client.get_historical_klines(
    "ETHUSDT", Client.KLINE_INTERVAL_1DAY, "7 days ago UTC"
)

# Websocket
twm.start_kline_socket(callback=handle_socket_message, symbol="BNBBTC")
sleep(4)
twm.stop()

# ========================
# Buying and selling crypto
# ========================
# Market orders
buy_quantity = get_valid_buy_quantity(client, "BNBUSDT", 1)
buy_order = client.order_market_buy(symbol="BNBUSDT", quantity=buy_quantity)
sell_order = client.order_market_sell(
    symbol="BNBUSDT", quantity=get_valid_sell_quantity(client, "BNBUSDT", buy_quantity)
)

# Limit orders
buy_order = client.order_limit_buy(symbol="BNBUSDT", quantity=0.1, price=500)

sleep(4)

print(f"Status of buy order: {buy_order['status']}")

client.cancel_order(symbol=buy_order["symbol"], orderId=buy_order["orderId"])

sell_order = client.order_limit_sell(symbol="BNBUSDT", quantity=0.1, price=800)

sleep(4)

print(f"Status of sell order: {sell_order['status']}")
client.cancel_order(symbol=sell_order["symbol"], orderId=sell_order["orderId"])

# ========================
# Transfering crypto
# ========================
result = client.withdraw(
    coin="BNB",
    address="0x73c3F0A96094E31fC3168f915e4Deb9D8Ff5239F",
    amount=0.01,
    network="BSC",
)
