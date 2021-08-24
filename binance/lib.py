import binance
from binance.spot import Spot
import datetime
import config
import pprint
import logging

pp = pprint.PrettyPrinter(indent=4)
_client = None

def _get_client():
    global _client
    if not config.API_KEY or not config.API_SECRET:
        raise ValueError("API Key or Secret is None")
    if not _client:
        _client = Spot(base_url=config.BASE_URL, key=config.API_KEY, secret=config.API_SECRET)
    return _client

def _spot_api_call(api, **args):
    try:
        return api(**args), None
    except binance.error.ClientError as err:
        logging.error(err)
        return None, "ClientError"
    except binance.error.ServerError as err:
        logging.error(err)
        return None, "ServerError"
    except Exception as err:
        logging.error(err)
        return None, "Error"

def _get_sym_for_quote_asset(quote_asset):
    _res, _err = _spot_api_call(_get_client().exchange_info)
    if _err is not None:
        logging.error("Got error while _get_sym_for_quote_asset", _err)
        return []
    symbols = _res["symbols"]
    result = []
    for symbol in symbols:
        if symbol["quoteAsset"] == quote_asset:
            result.append(symbol["symbol"])
    return result

def _get_total_value(trades):
    total = 0.0
    for trade in trades:
        total = total + (float(trade[0]) * float(trade[1]))
    return total

def highest_vol_quote_asset_symbols(quote_asset="BTC", limit=5):
    symbols, err = _get_sym_for_quote_asset(quote_asset)
    if err:
        return [], "Error getting symbols"
    volume_per_symbol = {}
    for symbol in symbols:
        try:
            one_day_ticker = _get_client().ticker_24hr(symbol)
            volume_per_symbol[symbol] = float(one_day_ticker["volume"])
        except binance.error.ClientError as err:
            logging.error(err)
            return [], "ClientError"
        except binance.error.ServerError as err:
            logging.error(err)
            return [], "ServerError"
        except Exception as err:
            logging.error(err)
            return [], "Error"
    sorted_trades = sorted(volume_per_symbol.items(), key=lambda item: item[1], reverse=True)
    return sorted_trades[:limit], None

def highest_trades_quote_asset_symbols(quote_asset="USDT", limit=5):
    symbols, err = _get_sym_for_quote_asset(quote_asset)
    if err:
        return [], "Error getting symbols"
    trades_per_symbol = {}
    for symbol in symbols:
        try:
            one_day_ticker = _get_client().ticker_24hr(symbol)
            trades_per_symbol[symbol] = one_day_ticker["count"]
        except binance.error.ClientError as err:
            logging.error(err)
            return [], "ClientError"
        except binance.error.ServerError as err:
            logging.error(err)
            return [], "ServerError"
        except Exception as err:
            logging.error(err)
            return [], "Error"
    sorted_trades = sorted(trades_per_symbol.items(), key=lambda item: item[1], reverse=True)
    return sorted_trades[:limit], None

def get_notaional_value_of_bids_and_asks(symbols, limit=200):
    if limit > 500:
        return [], "Limit should be less than 500"
    value_per_symbol = {}
    for symbol in symbols:
        try:
            depth = _get_client().depth(symbol, limit=limit)
            value_per_symbol[symbol] = [_get_total_value(depth["bids"]), _get_total_value(depth["asks"])]
        except binance.error.ClientError as err:
            logging.error(err)
            return [], "ClientError"
        except binance.error.ServerError as err:
            logging.error(err)
            return [], "ServerError"
        except Exception as err:
            logging.error(err)
            return [], "Error"
    return value_per_symbol, None

def get_price_spread(symbols):
    spread_per_symbol = {}
    for symbol in symbols:
        try:
            book_ticker = _get_client().book_ticker(symbol)
            spread_per_symbol[symbol] = float(book_ticker["bidPrice"]) - float(book_ticker["askPrice"])
        except binance.error.ClientError as err:
            logging.error(err)
            return [], "ClientError"
        except binance.error.ServerError as err:
            logging.error(err)
            return [], "ServerError"
        except Exception as err:
            logging.error(err)
            return [], "Error"
    return spread_per_symbol, None

# pp.pprint(highest_vol_quote_asset_symbols())
# pp.pprint(highest_trades_quote_asset_symbols())
symbols = _get_sym_for_quote_asset("BTC")
pp.pprint(symbols)
# pp.pprint(get_notaional_value_of_bids_and_asks(symbols))
# pp.pprint(get_price_spread(symbols))