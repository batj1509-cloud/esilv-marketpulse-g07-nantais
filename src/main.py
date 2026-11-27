
import json
from pathlib import Path

from analytics import (
    align_series,
    calculate_base_100,
    calculate_period_return,
    calculate_relative_performance,
)

# Yahoo provider (TD09)
from providers.yahoo_provider import (
    YAHOO_SYMBOLS,
    fetch_yahoo_prices,
)

# Bloomberg provider (TD10)
from providers.bloomberg_provider import (
    ACCESS_MODE,
    BLOOMBERG_IDENTIFIERS,
    fetch_approved_sample_prices,
)


DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "sample"

PERIOD = "1mo"
INTERVAL = "1d"


def load_instruments():
    with open(DATA_DIR / "instruments.json", encoding="utf-8") as file:
        return json.load(file)


# --------------------------------------------------
# PROVIDER FUNCTIONS
# --------------------------------------------------

def load_yahoo_prices(asset):
    """Load canonical prices from Yahoo Finance."""
    ticker = asset["ticker"]

    if ticker not in YAHOO_SYMBOLS:
        raise ValueError(f"No Yahoo symbol configured for {ticker}.")

    return fetch_yahoo_prices(
        YAHOO_SYMBOLS[ticker],
        ticker,
        PERIOD,
        INTERVAL,
    )


def load_bloomberg_prices(asset):
    """Load and normalize approved Bloomberg-stage prices."""
    ticker = asset["ticker"]

    if ticker not in BLOOMBERG_IDENTIFIERS:
        raise ValueError(f"No Bloomberg identifier configured for {ticker}.")

    provider_identifier = BLOOMBERG_IDENTIFIERS[ticker]

    if ACCESS_MODE == "APPROVED_SAMPLE":
        return fetch_approved_sample_prices(provider_identifier)

    if ACCESS_MODE == "LIVE":
        raise NotImplementedError(
            "LIVE Bloomberg acquisition must use the instructor-approved mechanism."
        )

    raise ValueError(f"Unsupported Bloomberg access mode: {ACCESS_MODE}")


# --------------------------------------------------
# SHARED APPLICATION SNAPSHOT
# --------------------------------------------------

def build_market_snapshot(
    instrument,
    benchmark,
    lookback=PERIOD,
    interval=INTERVAL,
):
    """
    Build the shared MarketPulse result.

    This function is imported by the TD11 dashboard.
    It contains no terminal-specific presentation.
    """

    instrument_prices = load_bloomberg_prices(instrument)
    benchmark_prices = load_bloomberg_prices(benchmark)

    aligned_instrument, aligned_benchmark = align_series(
        instrument_prices,
        benchmark_prices,
    )

    if not aligned_instrument:
        raise ValueError(
            "No common dates for the instrument and benchmark."
        )

    instrument_return = calculate_period_return(aligned_instrument)
    benchmark_return = calculate_period_return(aligned_benchmark)

    relative_performance = calculate_relative_performance(
        instrument_return,
        benchmark_return,
    )

    instrument_base_100 = calculate_base_100(aligned_instrument)
    benchmark_base_100 = calculate_base_100(aligned_benchmark)

    return {
        "provider": "Bloomberg",
        "access_mode": ACCESS_MODE,
        "lookback": lookback,
        "interval": interval,
        "instrument": instrument,
        "benchmark": benchmark,
        "instrument_prices": aligned_instrument,
        "benchmark_prices": aligned_benchmark,
        "instrument_return": instrument_return,
        "benchmark_return": benchmark_return,
        "relative_performance": relative_performance,
        "instrument_base_100": instrument_base_100,
        "benchmark_base_100": benchmark_base_100,
    }


# --------------------------------------------------
# TERMINAL DISPLAY FUNCTIONS
# --------------------------------------------------

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


# --------------------------------------------------
# MAIN APPLICATION
# --------------------------------------------------

def main():
    instruments = load_instruments()

    instrument = instruments["instrument"]
    benchmark = instruments["benchmark"]

    try:
        snapshot = build_market_snapshot(instrument, benchmark)
    except (ValueError, KeyError, NotImplementedError) as error:
        raise SystemExit(str(error)) from None

    print("=== MarketPulse ===")
    print()

    print(f"Provider    : {snapshot['provider']}")
    print(f"Access mode : {snapshot['access_mode']}")

    print()
    print("Market configuration")
    print(f"Period      : {snapshot['lookback']}")
    print(f"Interval    : {snapshot['interval']}")

    print()
    print("Instrument")
    display_market_summary(
        snapshot["instrument"],
        snapshot["instrument_prices"],
    )
    print(f"Period return: {snapshot['instrument_return']:+.2f}%")

    print()
    print("Benchmark")
    display_market_summary(
        snapshot["benchmark"],
        snapshot["benchmark_prices"],
        show_currency=False,
    )
    print(f"Period return: {snapshot['benchmark_return']:+.2f}%")

    print()
    print("Relative performance")
    print(
        f"{instrument['ticker']} vs {benchmark['ticker']}: "
        f"{snapshot['relative_performance']:+.2f} percentage points"
    )

    print()
    print("Base 100")

    for key in ("instrument_base_100", "benchmark_base_100"):
        series = snapshot[key]
        first, last = series[0], series[-1]

        print(
            f"{first['ticker']}: "
            f"{first['value']:.2f} -> {last['value']:.2f}"
        )


if __name__ == "__main__":
    main()
