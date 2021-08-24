import pprint
import argparse
from prometheus_client import start_http_server, Gauge

import lib
import config

pp = pprint.PrettyPrinter(indent=4)
parser = argparse.ArgumentParser(description='Binance exchange data')
parser.add_argument('-d','--data', help='Get data for q1, q2, q3, q4, q5 or q6. Default q1', default="q1")
args = vars(parser.parse_args())


def export_metrics(symbols):
    spread_metrics, delta_metrics = {}, {}
    for symbol in symbols:
        spread_metrics[symbol] = Gauge(f"spread_{symbol}", f"Spread for {symbol}")
        delta_metrics[symbol] = Gauge(f"delta_{symbol}", f"Delta for {symbol}")
    start_http_server(config.METRICS_SERVER_PORT)
    for spread_per_symbol in lib.get_periodic_spread(symbols=symbols):
        for symbol in spread_per_symbol:
            spread_metrics[symbol].set(spread_per_symbol[symbol]["s"])
            delta_metrics[symbol].set(spread_per_symbol[symbol]["d"])


if args["data"] == "q2":
    pp.pprint(lib.highest_trades_per_symbol(quote_asset="USDT", by="count"))
elif args["data"] == "q3":
    _res = lib.highest_trades_per_symbol(quote_asset="BTC", by="volume")
    if _res:
        symbols = [data[0] for data in _res]
        pp.pprint(lib.get_notaional_value_of_bids_and_asks(symbols))
elif args["data"] == "q4":
    _res = lib.highest_trades_per_symbol(quote_asset="USDT", by="count")
    if _res:
        symbols = [data[0] for data in _res]
        pp.pprint(lib.get_price_spread(symbols))
elif args["data"] == "q5":
    _res = lib.highest_trades_per_symbol(quote_asset="USDT", by="count")
    if _res:
        symbols = [data[0] for data in _res]
        for spread in lib.get_periodic_spread(symbols=symbols):
            pp.pprint(spread)
elif args["data"] == "q6":
    _res = lib.highest_trades_per_symbol(quote_asset="USDT", by="count")
    if _res:
        symbols = [data[0] for data in _res]
        export_metrics(symbols)
else:
    pp.pprint(lib.highest_trades_per_symbol(quote_asset="BTC", by="volume"))