import math

def format_number(value) -> str:
    try:
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return "N/A"
        return f"{value:,.2f}"
    except (TypeError, ValueError):
        return "N/A"

def format_percentage(value) -> str:
    try:
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return "N/A"
        sign = "+" if value >= 0 else ""
        return f"{sign}{value * 100:.2f}%"
    except (TypeError, ValueError):
        return "N/A"

def get_asset_name(assets_df, symbol: str) -> str:
    try:
        row = assets_df.loc[assets_df["symbol"] == symbol, "name"]
        if not row.empty:
            return row.iloc[0]
    except Exception:
        pass
    return symbol

def safe_round(value, digits: int = 2):
    try:
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return None
        return round(float(value), digits)
    except (TypeError, ValueError):
        return None
