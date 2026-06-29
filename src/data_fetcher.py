import pandas as pd
import yfinance as yf
import streamlit as st
from datetime import datetime

REQUIRED_COLUMNS = {"symbol", "name", "category", "description"}

def load_assets(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"assets.csv is missing columns: {missing}")
    return df.reset_index(drop=True)

def fetch_single_asset(symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
    raw = yf.download(symbol, period=period, interval=interval, progress=False, auto_adjust=True)
    if raw is None or raw.empty:
        raise ValueError(f"No data returned for {symbol}")
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)
    if "Close" not in raw.columns:
        raise ValueError(f"'Close' column missing for {symbol}")
    df = raw[["Close"]].copy()
    df.index.name = "Date"
    df = df.reset_index().dropna(subset=["Close"])
    if df.empty:
        raise ValueError(f"All Close prices are NaN for {symbol}")
    return df

@st.cache_data(ttl=3600)
def fetch_all_assets(symbols: tuple, names: tuple, categories: tuple, period: str = "1y", interval: str = "1d") -> tuple:
    frames = []
    failed = []
    for symbol, name, category in zip(symbols, names, categories):
        try:
            df = fetch_single_asset(symbol, period=period, interval=interval)
            df["symbol"] = symbol
            df["name"] = name
            df["category"] = category
            frames.append(df)
        except Exception:
            failed.append(symbol)
    fetched_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not frames:
        return pd.DataFrame(), failed, fetched_at
    combined = pd.concat(frames, ignore_index=True)
    combined["Date"] = pd.to_datetime(combined["Date"])
    return combined, failed, fetched_at
