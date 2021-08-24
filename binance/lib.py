import binance
from binance.spot import Spot
import datetime
import logging
import time

import config

_client = None


def _get_client():
    """Returns Spot API client

    Returns
    ------
    binance.spot Spot API client
    """
    global _client
    if not config.API_KEY or not config.API_SECRET:
        raise ValueError("API Key or Secret is None")
    if not _client:
        _client = Spot(base_url=config.BASE_URL, key=config.API_KEY, secret=config.API_SECRET)
    return _client


def _get_total_value(trades):
    """A trade has quantity and price. Total value returns quantity * price

    Parameters
    ----------
    trades : list
        list of trades where each trade is a list of quantity and price

    Returns
    ------
    float
    """
    total = 0.0
    for trade in trades:
        total = total + (float(trade[0]) * float(trade[1]))
    return total


def _spot_api_call(api, **args):
    try:
        return api(**args), None
    except binance.error.ClientError as err:
        return None, err
    except binance.error.ServerError as err:
        return None, err
    except Exception as err:
        return None, err


def get_sym_for_quote_asset(quote_asset="BTC"):
    """Returns all symbols whose quote asset is 'quote_asset'

    Parameters
    ----------
    quote_asset : str

    Returns
    ------
    list
        a list of symbols whose quote asset is 'quote_asset'
    """
    _res, _err = _spot_api_call(_get_client().exchange_info)
    if _err is not None:
        logging.error("Got error while get_sym_for_quote_asset", _err)
        return []
    symbols = _res["symbols"]
    result = []
    for symbol in symbols:
        if symbol["quoteAsset"] == quote_asset:
            result.append(symbol["symbol"])
    return result


def highest_trades_per_symbol(quote_asset="USDT", by="count", limit=5):
    """For all symbols whose quote asset is 'quote_asset', returns highest trades
    by volume or count

    Parameters
    ----------
    quote_asset : str
    by: str
        Aggregates results 'by' - can be volume or count
    limit : int
        Limit return result to these many symbols

    Returns
    ------
    list
        a list of tuples [(symbol, value)]
    """
    if by not in ["count", "volume"]:
        logging.error("highest_trades_per_symbol - can be aggregated based on count and volume only")
        return None
    symbols = get_sym_for_quote_asset(quote_asset)
    trades_per_symbol = {}
    for symbol in symbols:
        one_day_ticker, _err = _spot_api_call(_get_client().ticker_24hr, symbol=symbol)
        if _err is not None:
            logging.error(f"Got error while highest_trades_per_symbol for {symbol}", _err)
            return None
        trades_per_symbol[symbol] = float(one_day_ticker[by])
    sorted_trades = sorted(trades_per_symbol.items(), key=lambda item: item[1], reverse=True)
    return sorted_trades[:limit]


def get_notaional_value_of_bids_and_asks(symbols, limit=200):
    """For all symbols 'symbols' returns notational values for bids
    and asks for most recent 'limit' orders

    Parameters
    ----------
    symbols : list
        List of symbols
    limit : int
        Limit to these many recent orders

    Returns
    ------
    dict
        a dict of values per symbol. e.g: {"BNBBTC": [total_bid_value, total_ask_value]}
    """
    if limit > 500:
        return [], "Limit should be less than 500"
    value_per_symbol = {}
    for symbol in symbols:
        depth, _err = _spot_api_call(_get_client().depth, symbol=symbol, limit=limit)
        if _err is not None:
            logging.error(f"Got error while get_notaional_value_of_bids_and_asks for {symbol}", _err)
            return {}
        value_per_symbol[symbol] = [_get_total_value(depth["bids"]), _get_total_value(depth["asks"])]
    return value_per_symbol


def get_price_spread(symbols):
    """Get price spread for 'symbols'

    Parameters
    ----------
    symbols : list
        List of symbols

    Returns
    ------
    dict
        a dict of spread per symbol. e.g: {"BNBBTC": 12}
    """
    spread_per_symbol = {}
    for symbol in symbols:
        book_ticker, _err = _spot_api_call(_get_client().book_ticker, symbol=symbol)
        if _err is not None:
            logging.error(f"Got error while get_price_spread for {symbol}", _err)
            return {}
        spread_per_symbol[symbol] = float(book_ticker["bidPrice"]) - float(book_ticker["askPrice"])
    return spread_per_symbol


def get_spread_and_delta(curr_spread_per_sym, prev_spread_per_sym):
    """Returns absolute delta of spread by comparing current and previous spread

    Parameters
    ----------
    curr_spread_per_sym : dict
        a dict of spread per symbol
    prev_spread_per_sym : dict
        a dict of spread per symbol

    Returns
    ------
    dict
        a dict of spread and delta per symbol. e.g: {"BNBBTC": {"s": 1.2, "d": 0.2}}.
        Where 's' is key for spread and 'd' for delta
    """
    res = {}
    if not prev_spread_per_sym:
        prev_spread_per_sym = curr_spread_per_sym
    for symbol in curr_spread_per_sym:
        delta = curr_spread_per_sym[symbol] - prev_spread_per_sym[symbol]
        if delta < 0:
            delta = -1 * delta
        res[symbol] = {"s": curr_spread_per_sym[symbol], "d": delta}
    return res


def get_periodic_spread(symbols, period=10):
    """A generator to generate spread and delta every 'period' seconds for 'symbols' symbols

    Parameters
    ----------
    symbols : list
    period : int

    Yields
    ------
    dict
        a dict of spread and delta per symbol. e.g: {"BNBBTC": {"s": 1.2, "d": 0.2}}.
        Where 's' is key for spread and 'd' for delta
    """
    starttime = time.time()
    prev_spread, curr_spread = None, None
    while True:
        prev_spread = curr_spread
        curr_spread = get_price_spread(symbols)
        yield get_spread_and_delta(curr_spread, prev_spread)
        time.sleep(period - ((time.time() - starttime) % period))