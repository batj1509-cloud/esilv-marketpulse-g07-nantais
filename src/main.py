from pathlib import Path
import json

from analytics import (
    align_series,
    calculate_base_100,
    calculate_period_return,
    calculate_relative_performance,
)
from providers.yahoo_provider import YAHOO_SYMBOLS, fetch_yahoo_prices


DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "sample"

PERIOD = "1mo"
INTERVAL = "1d"


def load_instruments():
    with open(DATA_DIR / "instruments.json", encoding="utf-8") as file:
        return json.load(file)


def load_yahoo_prices(asset):
    ticker = asset["ticker"]
    return fetch_yahoo_prices(YAHOO_SYMBOLS[ticker], ticker, PERIOD, INTERVAL)


def get_first_close(prices):
    return float(prices[0]["close"])


def get_last_close(prices):
    return float(prices[-1]["close"])


def get_first_date(prices):
    return prices[0]["date"]


def get_last_date(prices):
    return prices[-1]["date"]


def display_market_summary(asset, prices, show_currency=True):
    currency = f" {asset['currency']}" if show_currency else ""
    print(f"{asset['ticker']} - {asset['name']}")
    print(f"Observations : {len(prices)}")
    print(f"First date   : {get_first_date(prices)}")
    print(f"Last date    : {get_last_date(prices)}")
    print(f"First close  : {get_first_close(prices):.2f}{currency}")
    print(f"Last close   : {get_last_close(prices):.2f}{currency}")


def main():
    instruments = load_instruments()

    instrument = instruments["instrument"]
    benchmark = instruments["benchmark"]

    try:
        instrument_prices = load_yahoo_prices(instrument)
        benchmark_prices = load_yahoo_prices(benchmark)
    except ValueError as error:
        raise SystemExit(str(error)) from None
    aligned_instrument, aligned_benchmark = align_series(
        instrument_prices, benchmark_prices,
    )
    if not aligned_instrument:
        raise SystemExit("No common dates for the instrument and benchmark.")

    instrument_return = calculate_period_return(aligned_instrument)
    benchmark_return = calculate_period_return(aligned_benchmark)
    relative_performance = calculate_relative_performance(
        instrument_return, benchmark_return,
    )
    instrument_base = calculate_base_100(aligned_instrument)
    benchmark_base = calculate_base_100(aligned_benchmark)

    print("=== MarketPulse ===")
    print()
    print("Provider : Yahoo Finance via yfinance")
    print("Market configuration")
    print(f"Period   : 1 month ({PERIOD})")
    print(f"Interval : Daily ({INTERVAL})")
    print()
    print("Instrument")
    display_market_summary(instrument, aligned_instrument)
    print(f"Period return: {instrument_return:+.2f}%")
    print()
    print("Benchmark")
    display_market_summary(benchmark, aligned_benchmark, show_currency=False)
    print(f"Period return: {benchmark_return:+.2f}%")
    print()
    print("Relative performance")
    print(
        f"{instrument['ticker']} vs {benchmark['ticker']}: "
        f"{relative_performance:+.2f} percentage points"
    )
    print()
    print("Base 100")
    for series in (instrument_base, benchmark_base):
        first, last = series[0], series[-1]
        print(f"{first['ticker']}: {first['value']:.2f} -> {last['value']:.2f}")


if __name__ == "__main__":
    main()
