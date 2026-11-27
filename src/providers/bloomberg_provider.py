
import json
from pathlib import Path


BLOOMBERG_IDENTIFIERS = {
    "AAPL": "AAPL US Equity",
    "SP500": "SPX Index",
}

ACCESS_MODE = "APPROVED_SAMPLE"

REFERENCE_SAMPLE = (
    Path(__file__).resolve().parents[2]
    / "data"
    / "sample"
    / "bloomberg_reference_sample.json"
)


def load_bloomberg_reference_sample(path=REFERENCE_SAMPLE):
    with open(path, encoding="utf-8") as file:
        return json.load(file)


def find_reference_series(payload, provider_identifier):
    for series in payload["series"]:
        if series["provider_identifier"] == provider_identifier:
            return series

    raise ValueError(
        "Approved Bloomberg-stage series not found: "
        f"{provider_identifier}"
    )


def normalize_reference_series(series):
    canonical_ticker = series["canonical_ticker"]
    rows = []

    for observation in series["observations"]:
        rows.append({
            "date": observation["observation_date"],
            "ticker": canonical_ticker,
            "open": float(observation["open_value"]),
            "high": float(observation["high_value"]),
            "low": float(observation["low_value"]),
            "close": float(observation["close_value"]),
            "volume": int(observation["volume_value"]),
        })

    return rows


def fetch_approved_sample_prices(provider_identifier):
    payload = load_bloomberg_reference_sample()

    if payload["access_mode"] != "approved_sample":
        raise ValueError("The Bloomberg fixture is not an approved sample.")

    series = find_reference_series(payload, provider_identifier)

    return normalize_reference_series(series)


def fetch_raw_bloomberg_history(identifier, start_date, end_date):
    raise NotImplementedError(
        "LIVE Bloomberg access requires the instructor-approved environment."
    )
