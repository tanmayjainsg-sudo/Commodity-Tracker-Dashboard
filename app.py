import os
import pandas as pd
import streamlit as st
from src.config import APP_TITLE, APP_SUBTITLE, CATEGORY_ORDER
from src.data_fetcher import load_assets, fetch_all_assets
from src.calculations import calculate_asset_metrics, calculate_category_performance, get_top_movers, normalize_prices, calculate_correlation
from src.charts import create_price_chart, create_normalized_comparison_chart, create_returns_bar_chart, create_category_bar_chart, create_heatmap
from src.market_note import generate_weekly_note
from src.utils import format_number, format_percentage

st.set_page_config(page_title=APP_TITLE, layout="wide", page_icon="📈")

with st.sidebar:
    st.title(f"📈 {APP_TITLE}")
    st.caption(APP_SUBTITLE)
    st.divider()
    period = st.selectbox("Data Period", options=["3mo", "6mo", "1y", "2y", "5y"], index=2)
    return_metric = st.selectbox("Return Metric", options=["return_1d","return_1w","return_1m","return_3m","return_6m"], format_func=lambda x: {"return_1d":"1-Day","return_1w":"1-Week","return_1m":"1-Month","return_3m":"3-Month","return_6m":"6-Month"}[x], index=1)
    ma_window = st.selectbox("Moving Average Window", options=[50, 100, 200], index=0, format_func=lambda x: f"{x}-Day MA")
    st.divider()
    st.info("📡 Market data is cached for 1 hour.")

ASSETS_PATH = os.path.join(os.path.dirname(__file__), "data", "assets.csv")
try:
    assets_df = load_assets(ASSETS_PATH)
except Exception as e:
    st.error(f"Failed to load assets.csv: {e}")
    st.stop()

available_categories = [c for c in CATEGORY_ORDER if c in assets_df["category"].unique()]
with st.sidebar:
    selected_categories = st.multiselect("Filter Categories", options=available_categories, default=available_categories)

filtered_assets = assets_df[assets_df["category"].isin(selected_categories)]

with st.spinner("Fetching market data…"):
    price_df, failed_symbols, fetched_at = fetch_all_assets(symbols=tuple(filtered_assets["symbol"].tolist()), names=tuple(filtered_assets["name"].tolist()), categories=tuple(filtered_assets["category"].tolist()), period=period)

if failed_symbols:
    failed_names = filtered_assets.loc[filtered_assets["symbol"].isin(failed_symbols), "name"].tolist()
    st.warning(f"⚠️ Could not fetch data for: {', '.join(failed_names or failed_symbols)}. These assets have been skipped.")

if price_df.empty:
    st.error("No market data could be loaded. Please try again later.")
    st.stop()

metrics_df = calculate_asset_metrics(price_df, filtered_assets, ma_window=ma_window)
category_df = calculate_category_performance(metrics_df)
st.caption(f"🕒 Data last updated: {fetched_at}")

st.title(f"📈 {APP_TITLE}")
st.caption(APP_SUBTITLE)
st.divider()

tab1, tab2, tab3, tab4, tab5 = st.tabs(["🌍 Market Overview", "🔍 Asset Deep Dive", "🔗 Cross-Market Comparison", "📝 Weekly Market Note", "ℹ️ About"])

with tab1:
    st.subheader("Market Snapshot")
    gainers, losers = get_top_movers(metrics_df, return_col="return_1w", n=1)
    best = gainers.iloc[0] if not gainers.empty else None
    worst = losers.iloc[0] if not losers.empty else None
    most_volatile = metrics_df.dropna(subset=["volatility_30d"]).sort_values("volatility_30d", ascending=False).iloc[0] if not metrics_df.dropna(subset=["volatility_30d"]).empty else None
    best_cat = category_df.dropna(subset=["avg_return_1w"]).sort_values("avg_return_1w", ascending=False).iloc[0] if not category_df.dropna(subset=["avg_return_1w"]).empty else None
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🏆 Best (1W)", best["name"] if best is not None else "N/A", format_percentage(best["return_1w"]) if best is not None else "N/A")
    c2.metric("📉 Worst (1W)", worst["name"] if worst is not None else "N/A", format_percentage(worst["return_1w"]) if worst is not None else "N/A")
    c3.metric("⚡ Most Volatile", most_volatile["name"] if most_volatile is not None else "N/A", f"{most_volatile['volatility_30d']*100:.1f}% ann." if most_volatile is not None else "N/A")
    c4.metric("📦 Top Category (1W)", best_cat["category"] if best_cat is not None else "N/A", format_percentage(best_cat["avg_return_1w"]) if best_cat is not None else "N/A")
    st.divider()
    st.subheader("Asset Metrics")
    display_df = metrics_df.copy()
    for col in ["return_1d","return_1w","return_1m","return_3m","return_6m","volatility_30d"]:
        display_df[col] = display_df[col].apply(format_percentage)
    display_df["latest_price"] = display_df["latest_price"].apply(format_number)
    display_df["above_ma"] = display_df["above_ma"].apply(lambda x: "✅" if x is True else ("❌" if x is False else "—"))
    rename_map = {"category":"Category","name":"Asset","latest_price":"Latest Price","return_1d":"1D","return_1w":"1W","return_1m":"1M","return_3m":"3M","return_6m":"6M","volatility_30d":"30D Vol","above_ma":f"Above {ma_window}D MA"}
    st.dataframe(display_df.rename(columns=rename_map)[list(rename_map.values())], use_container_width=True, hide_index=True)
    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Returns by Asset")
        st.plotly_chart(create_returns_bar_chart(metrics_df, return_metric), use_container_width=True)
    with col_b:
        st.subheader("Category Performance (1W)")
        st.plotly_chart(create_category_bar_chart(category_df), use_container_width=True)
    st.subheader("Performance Heatmap")
    st.plotly_chart(create_heatmap(metrics_df), use_container_width=True)

with tab2:
    st.subheader("Asset Deep Dive")
    asset_options = metrics_df["name"].tolist()
    if not asset_options:
        st.warning("No asset data available.")
    else:
        selected_name = st.selectbox("Select an asset", options=asset_options)
        selected_row = metrics_df[metrics_df["name"] == selected_name].iloc[0]
        selected_symbol = selected_row["symbol"]
        c1,c2,c3,c4,c5 = st.columns(5)
        c1.metric("Latest Price", format_number(selected_row["latest_price"]))
        c2.metric("1W Return", format_percentage(selected_row["return_1w"]))
        c3.metric("1M Return", format_percentage(selected_row["return_1m"]))
        c4.metric("30D Volatility", f"{selected_row['volatility_30d']*100:.1f}%" if selected_row["volatility_30d"] else "N/A")
        c5.metric(f"vs {ma_window}D MA", "✅ Above" if selected_row["above_ma"] is True else ("❌ Below" if selected_row["above_ma"] is False else "—"))
        asset_prices = price_df[price_df["symbol"] == selected_symbol].sort_values("Date")
        st.plotly_chart(create_price_chart(asset_prices, selected_name), use_container_width=True)
        st.subheader("Recent Closing Prices (Last 14 Days)")
        recent = asset_prices[["Date","Close"]].tail(14).sort_values("Date", ascending=False).copy()
        recent["Date"] = recent["Date"].dt.strftime("%Y-%m-%d")
        recent["Close"] = recent["Close"].apply(format_number)
        st.dataframe(recent, use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Cross-Market Comparison")
    all_names = metrics_df["name"].tolist()
    if len(all_names) < 2:
        st.warning("Need at least two assets for comparison.")
    else:
        col_a, col_b = st.columns(2)
        with col_a:
            asset_a_name = st.selectbox("Asset A", options=all_names, index=0, key="cmp_a")
        with col_b:
            asset_b_name = st.selectbox("Asset B", options=all_names, index=1, key="cmp_b")
        sym_a = metrics_df.loc[metrics_df["name"]==asset_a_name,"symbol"].iloc[0]
        sym_b = metrics_df.loc[metrics_df["name"]==asset_b_name,"symbol"].iloc[0]
        if sym_a == sym_b:
            st.warning("Please select two different assets.")
        else:
            norm_df = normalize_prices(price_df[price_df["symbol"].isin([sym_a, sym_b])].copy())
            if not norm_df.empty:
                st.plotly_chart(create_normalized_comparison_chart(norm_df), use_container_width=True)
            corr = calculate_correlation(price_df, sym_a, sym_b)
            if corr is not None:
                st.metric("Daily Return Correlation", f"{corr:.3f}")
                st.caption(
                    "Correlation measures how the two assets' daily returns move relative to each other, "
                    "on a scale from −1 to +1. Values near +1 mean they tend to rise and fall together; "
                    "near 0 means little relationship; near −1 means they tend to move in opposite directions. "
                    "Daily returns are used rather than raw prices to isolate genuine co-movement from shared long-term trends."
                )
                if corr > 0.6:
                    st.info("📊 These assets have moved **strongly together** over the selected period.")
                elif corr > 0.2:
                    st.info("📊 These assets have shown a **moderate positive relationship**.")
                elif corr >= -0.2:
                    st.info("📊 These assets have had **little linear relationship**.")
                else:
                    st.info("📊 These assets have moved **inversely** over the selected period.")

with tab4:
    st.subheader("Weekly Market Note")
    note_text = generate_weekly_note(metrics_df, category_df)
    st.markdown(note_text)
    st.caption("**How this note is generated:** it is built programmatically from the same live metrics shown elsewhere in the dashboard, not by a language model. It identifies the strongest and weakest performers and categories, then fills these figures into structured sentence templates. Some sections use simple conditional logic, for example the metals commentary compares gold and copper to flag a risk-on or risk-off tilt. Because it is rule-based, the same data always produces the same note, with no external API required.")
    st.divider()
    st.download_button("⬇️ Download Note as .txt", data=note_text.replace("**", "").replace("*", ""), file_name="commodity_pulse_weekly_note.txt", mime="text/plain")

with tab5:
    st.subheader("About This Project")
    st.markdown("""
### My background

I'm a Computer Engineering student who's been drawn to finance for about as long as I can remember. I figured out I had an affinity for markets early. As a kid I used to trade and sell football cards, and I noticed I cared less about the cards themselves than about reading the spread between what people would buy and sell at.

I chose Computer Engineering over Computer Science deliberately. I knew I didn't want to live purely in software. I wanted to sit at the intersection of technology and the physical world, and finance is where my real interest lies. Tech is the infrastructure of the future; commodities are the thing being moved, priced, and fought over underneath it.

### Why commodities

Growing up, I had exposure to the world of petrochemical shipping, so oil and natural gas were familiar topics long before they were chart lines to me. That's why this dashboard leans into energy and physical commodities rather than just tracking equities: Brent, WTI, natural gas, and the FX pairs (USD/SGD, USD/MYR) that matter to trade flows around Southeast Asia.

I built it in Python, the first language I ever learned and still the one I reach for first.

### Why this project matters

Commodity markets sit underneath almost everything else in the economy. Energy prices feed into transport, manufacturing, and ultimately the cost of nearly every good that moves through a port. Agricultural prices shape food costs for billions of people. Industrial metals like copper act as a real-time read on global growth. Tracking these markets together, alongside FX and macro benchmarks, gives a fuller picture of how the physical economy is actually moving than any single asset class can on its own.

For me, building this was a way to connect the technical skills I'm developing in Computer Engineering with the markets I've cared about since I was a kid. It's a small step toward the kind of work I want to do: using technology to understand and operate in physical, real-world markets.

### What it does

This dashboard pulls market data via `yfinance` refreshed hourly, calculates multi-period returns and annualized volatility, ranks the biggest movers, compares cross-asset relationships, and generates a simple weekly market note.

---
*This is a portfolio and learning project. Not investment advice.*
""")