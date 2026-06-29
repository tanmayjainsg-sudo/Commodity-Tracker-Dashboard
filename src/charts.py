import plotly.graph_objects as go
import plotly.express as px

_LAYOUT = dict(font=dict(family="Inter, Arial, sans-serif", size=13), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", margin=dict(l=40, r=20, t=50, b=40), hovermode="x unified")

def create_price_chart(asset_df, asset_name):
    df = asset_df.sort_values("Date").copy()
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Date"], y=df["Close"], mode="lines", name="Price", line=dict(color="#4C78A8", width=2)))
    if len(df) >= 20:
        df["MA20"] = df["Close"].rolling(20).mean()
        fig.add_trace(go.Scatter(x=df["Date"], y=df["MA20"], mode="lines", name="20-Day MA", line=dict(color="#F58518", width=1.5, dash="dot")))
    if len(df) >= 50:
        df["MA50"] = df["Close"].rolling(50).mean()
        fig.add_trace(go.Scatter(x=df["Date"], y=df["MA50"], mode="lines", name="50-Day MA", line=dict(color="#E45756", width=1.5, dash="dash")))
    fig.update_layout(title=f"{asset_name} — Price History", xaxis_title="Date", yaxis_title="Price", legend=dict(orientation="h", y=-0.15), **_LAYOUT)
    return fig

def create_normalized_comparison_chart(comparison_df):
    fig = px.line(comparison_df, x="Date", y="normalized", color="name", title="Normalized Performance Comparison (Base = 100)", labels={"normalized": "Indexed Price (Base 100)", "name": "Asset"})
    fig.update_layout(**_LAYOUT)
    return fig

def create_returns_bar_chart(metrics_df, return_col):
    label_map = {"return_1d": "1-Day Return", "return_1w": "1-Week Return", "return_1m": "1-Month Return", "return_3m": "3-Month Return", "return_6m": "6-Month Return"}
    df = metrics_df.dropna(subset=[return_col]).sort_values(return_col).copy()
    df["pct"] = df[return_col] * 100
    colors = ["#E45756" if v < 0 else "#54A24B" for v in df["pct"]]
    fig = go.Figure(go.Bar(
        x=df["pct"], y=df["name"], orientation="h",
        marker_color=colors,
        text=[f"{v:+.2f}%" for v in df["pct"]],
        textposition="inside",
        insidetextanchor="middle",
        textfont=dict(color="white", size=12),
    ))
    fig.update_layout(title=label_map.get(return_col, return_col), xaxis_title="Return (%)", yaxis_title="", **_LAYOUT)
    return fig

def create_category_bar_chart(category_df):
    df = category_df.dropna(subset=["avg_return_1w"]).sort_values("avg_return_1w").copy()
    df["pct"] = df["avg_return_1w"] * 100
    colors = ["#E45756" if v < 0 else "#4C78A8" for v in df["pct"]]
    fig = go.Figure(go.Bar(x=df["category"], y=df["pct"], marker_color=colors, text=[f"{v:+.2f}%" for v in df["pct"]], textposition="auto"))
    fig.update_layout(title="Average 1-Week Return by Category", xaxis_title="Category", yaxis_title="Avg Return (%)", **_LAYOUT)
    return fig

def create_heatmap(metrics_df):
    return_cols = ["return_1d", "return_1w", "return_1m", "return_3m", "return_6m"]
    df = metrics_df[["name"] + return_cols].copy().set_index("name") * 100
    z = df.values.tolist()
    text = [[f"{v:+.2f}%" if v == v else "N/A" for v in row] for row in z]
    fig = go.Figure(go.Heatmap(z=z, x=["1D","1W","1M","3M","6M"], y=df.index.tolist(), text=text, texttemplate="%{text}", colorscale="RdYlGn", zmid=0, colorbar=dict(title="Return %")))
    fig.update_layout(title="Performance Heatmap (%)", xaxis_title="Return Window", margin=dict(l=160, r=20, t=50, b=40), font=dict(family="Inter, Arial, sans-serif", size=12), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    return fig
