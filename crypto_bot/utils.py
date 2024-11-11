import math
from typing import Any

from binance.client import Client


def get_symbol_info(client: Client, trading_pair: str) -> dict[str, Any]:
    """Returns useful symbol info and filters.

    Args:
        client: Binance client
        trading_pair: trading pair to query, e.g. BNBUSDT

    Returns:
        dict containing useful filters, such as precision, lot size and notional
    """
    full_symbol_info = client.get_symbol_info(trading_pair)
    if not full_symbol_info:
        raise ValueError(f"Did not find pair {trading_pair}")

    symbol_info = {"precision": full_symbol_info["quotePrecision"]}
    filters = {f["filterType"]: f for f in full_symbol_info["filters"]}

    symbol_info["lot_size"] = {
        "min": float(filters["LOT_SIZE"]["minQty"]),
        "max": float(filters["LOT_SIZE"]["maxQty"]),
        "step": float(filters["LOT_SIZE"]["stepSize"]),
    }
    symbol_info["notional"] = {
        "min": float(filters["NOTIONAL"]["minNotional"]),
        "max": float(filters["NOTIONAL"]["maxNotional"]),
    }

    return symbol_info


def get_valid_buy_quantity(
    client: Client, trading_pair: str, desired_value_quote: float
) -> float:
    """Converts the desired buy value to an allowed one
    respecting all filters.

    Args:
        client: Binance client
        trading_pair: trading pair to buy (e.g. BNBUSDT)
        desired_value_base: amount to buy in QUOTE value (e.g. USDT)

    Returns:
        fixed buy value as base quantity (e.g. BNB)
    """
    symbol_info = get_symbol_info(client, trading_pair)

    current_price = float(client.get_symbol_ticker(symbol=trading_pair)["price"])
    buy_quantity = desired_value_quote / current_price

    # Clip to [min, max] notional value
    buy_quantity = max(buy_quantity, symbol_info["notional"]["min"] / current_price)
    buy_quantity = min(buy_quantity, symbol_info["notional"]["max"] / current_price)

    # Round to precision
    buy_quantity = round(buy_quantity, symbol_info["precision"])

    # Clip to [min, max] lot size, round to step size
    buy_quantity = round(
        buy_quantity, int(math.log10(1 / symbol_info["lot_size"]["step"]))
    )
    buy_quantity = max(buy_quantity, symbol_info["lot_size"]["min"])
    buy_quantity = min(buy_quantity, symbol_info["lot_size"]["max"])

    print(
        f"Requested buying {desired_value_quote} QUOTE of {trading_pair}. Adhering to filters gave a post-processed value of {buy_quantity} BASE, equal to approximately {buy_quantity * current_price} QUOTE"
    )

    return buy_quantity


def get_valid_sell_quantity(
    client: Client, trading_pair: str, desired_sell_quantiy: float
) -> float:
    """Converts the requested sell quantity into an allowed one respecting all filters.

    Args:
        client : Binance client
        trading_pair: trading pair to sell (e.g. BNBUSDT)
        desired_sell_quantiy: desired amount to sell in BASE

    Returns:
        fixed amount to sell in BASE
    """
    symbol_info = get_symbol_info(client, trading_pair)

    current_price = float(client.get_symbol_ticker(symbol=trading_pair)["price"])

    # Clip to [min, max] notional value
    sell_quantity = max(
        desired_sell_quantiy, symbol_info["notional"]["min"] / current_price
    )
    sell_quantity = min(sell_quantity, symbol_info["notional"]["max"] / current_price)

    # Round to precision
    sell_quantity = round(sell_quantity, symbol_info["precision"])

    # Clip to [min, max] lot size, round to step size
    sell_quantity = round(
        sell_quantity, int(math.log10(1 / symbol_info["lot_size"]["step"]))
    )
    sell_quantity = max(sell_quantity, symbol_info["lot_size"]["min"])
    sell_quantity = min(sell_quantity, symbol_info["lot_size"]["max"])

    print(
        f"Requested selling {desired_sell_quantiy} {trading_pair}. Adhering to filters gave a post-processed value of {sell_quantity}, equal to approximately {sell_quantity * current_price} BASE"
    )

    return sell_quantity
