import pandas as pd
import numpy as np
from src.calculations import (
    calculate_return,
    calculate_asset_metrics,
    calculate_category_performance,
    get_top_movers,
    normalize_prices,
    calculate_correlation,
)


# --- calculate_return ---

def test_calculate_return_basic():
    # 100 -> 110 over 1 period = 10% = 0.1
    s = pd.Series([100, 110])
    assert calculate_return(s, 1) == 0.1

def test_calculate_return_too_short():
    # only 1 data point, can't compute a 1-period return
    s = pd.Series([100])
    assert calculate_return(s, 1) is None

def test_calculate_return_handles_nan():
    # NaN should be dropped before calculating
    s = pd.Series([100, np.nan, 120])
    assert calculate_return(s, 1) == 0.2

def test_calculate_return_zero_start():
    # starting price of 0 would divide by zero -> None
    s = pd.Series([0, 50])
    assert calculate_return(s, 1) is None


# --- normalize_prices ---

def test_normalize_prices_starts_at_100():
    df = pd.DataFrame({
        "Date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
        "Close": [50, 75, 100],
        "symbol": ["TEST", "TEST", "TEST"],
    })
    result = normalize_prices(df)
    # first value should be normalized to 100
    assert result["normalized"].iloc[0] == 100
    # 75 is 1.5x of 50, so normalized should be 150
    assert result["normalized"].iloc[1] == 150


# --- calculate_correlation ---

def test_correlation_perfectly_positive():
    # two series that move identically should have correlation ~1.0
    dates = pd.to_datetime(pd.date_range("2024-01-01", periods=20))
    df = pd.DataFrame({
        "Date": list(dates) + list(dates),
        "Close": list(range(100, 120)) + list(range(200, 240, 2)),
        "symbol": ["A"] * 20 + ["B"] * 20,
    })
    corr = calculate_correlation(df, "A", "B")
    assert corr is not None
    assert round(corr, 2) == 1.0

def test_correlation_missing_symbol():
    df = pd.DataFrame({
        "Date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
        "Close": [100, 110],
        "symbol": ["A", "A"],
    })
    # symbol "B" doesn't exist -> None
    assert calculate_correlation(df, "A", "B") is None
