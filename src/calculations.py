import numpy as np
import pandas as pd

def calculate_return(series: pd.Series, periods: int):
    clean = series.dropna()
    if len(clean) <= periods:
        return None
    end = clean.iloc[-1]
    start = clean.iloc[-(periods + 1)]
    if start == 0:
        return None
    return (end - start) / start

def calculate_asset_metrics(price_df: pd.DataFrame, assets_df: pd.DataFrame, ma_window: int = 50) -> pd.DataFrame:
    records = []
    for _, asset_row in assets_df.iterrows():
        symbol = asset_row["symbol"]
        subset = price_df[price_df["symbol"] == symbol].sort_values("Date")
        if subset.empty:
            continue
        close = subset["Close"].reset_index(drop=True)
        latest_price = close.iloc[-1] if len(close) >= 1 else None
        daily_returns = close.pct_change().dropna()
        vol_30d = daily_returns.tail(30).std() * np.sqrt(252) if len(daily_returns) >= 5 else None
        ma_20 = close.tail(20).mean() if len(close) >= 20 else None
        ma_long = close.tail(ma_window).mean() if len(close) >= ma_window else None
        above_ma = bool(latest_price > ma_long) if (latest_price is not None and ma_long is not None) else None
        records.append({
            "symbol": symbol, "name": asset_row["name"], "category": asset_row["category"],
            "latest_price": latest_price,
            "return_1d": calculate_return(close, 1), "return_1w": calculate_return(close, 5),
            "return_1m": calculate_return(close, 21), "return_3m": calculate_return(close, 63),
            "return_6m": calculate_return(close, 126),
            "volatility_30d": vol_30d, "ma_20": ma_20, "ma_long": ma_long, "above_ma": above_ma })
    return pd.DataFrame(records)

def calculate_category_performance(metrics_df: pd.DataFrame) -> pd.DataFrame:
    return metrics_df.groupby("category")[["return_1w", "return_1m"]].mean().reset_index().rename(
        columns={"return_1w": "avg_return_1w", "return_1m": "avg_return_1m"})

def get_top_movers(metrics_df: pd.DataFrame, return_col: str = "return_1w", n: int = 3):
    valid = metrics_df.dropna(subset=[return_col]).sort_values(return_col)
    return valid.tail(n).iloc[::-1], valid.head(n)

def normalize_prices(df: pd.DataFrame) -> pd.DataFrame:
    frames = []
    for symbol, group in df.groupby("symbol"):
        g = group.sort_values("Date").copy()
        first_valid = g["Close"].dropna()
        if first_valid.empty:
            continue
        g["normalized"] = g["Close"] / first_valid.iloc[0] * 100
        frames.append(g)
    return pd.concat(frames, ignore_index=True) if frames else pd.DataFrame()

def calculate_correlation(df: pd.DataFrame, symbol_a: str, symbol_b: str):
    pivoted = df.pivot_table(index="Date", columns="symbol", values="Close")
    cols = [c for c in [symbol_a, symbol_b] if c in pivoted.columns]
    if len(cols) < 2:
        return None
    returns = pivoted[cols].pct_change().dropna()
    if len(returns) < 10:
        return None
    corr = returns[symbol_a].corr(returns[symbol_b])
    return float(corr) if not np.isnan(corr) else None
