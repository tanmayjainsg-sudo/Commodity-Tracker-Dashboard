import math

def format_pct(value) -> str:
    try:
        if value is None or (isinstance(value, float) and math.isnan(value)):
            return "N/A"
        sign = "+" if value >= 0 else ""
        return f"{sign}{value * 100:.2f}%"
    except (TypeError, ValueError):
        return "N/A"

def _get_metric(metrics_df, symbol, col):
    row = metrics_df.loc[metrics_df["symbol"] == symbol, col]
    if not row.empty:
        v = row.iloc[0]
        return None if (isinstance(v, float) and math.isnan(v)) else v
    return None

def generate_weekly_note(metrics_df, category_df) -> str:
    if metrics_df.empty:
        return "Insufficient data to generate a market note."
    valid = metrics_df.dropna(subset=["return_1w"])
    if valid.empty:
        best_row = worst_row = None
    else:
        best_row = valid.loc[valid["return_1w"].idxmax()]
        worst_row = valid.loc[valid["return_1w"].idxmin()]
    best_name = best_row["name"] if best_row is not None else "N/A"
    best_ret = format_pct(best_row["return_1w"]) if best_row is not None else "N/A"
    worst_name = worst_row["name"] if worst_row is not None else "N/A"
    worst_ret = format_pct(worst_row["return_1w"]) if worst_row is not None else "N/A"
    cat_valid = category_df.dropna(subset=["avg_return_1w"])
    if not cat_valid.empty:
        best_cat_row = cat_valid.loc[cat_valid["avg_return_1w"].idxmax()]
        worst_cat_row = cat_valid.loc[cat_valid["avg_return_1w"].idxmin()]
        best_cat, worst_cat = best_cat_row["category"], worst_cat_row["category"]
        best_cat_ret, worst_cat_ret = format_pct(best_cat_row["avg_return_1w"]), format_pct(worst_cat_row["avg_return_1w"])
    else:
        best_cat = worst_cat = best_cat_ret = worst_cat_ret = "N/A"
    brent_ret = _get_metric(metrics_df, "BZ=F", "return_1w")
    brent_1m = _get_metric(metrics_df, "BZ=F", "return_1m")
    wti_ret = _get_metric(metrics_df, "CL=F", "return_1w")
    zl_ret = _get_metric(metrics_df, "ZL=F", "return_1w")
    zl_1m = _get_metric(metrics_df, "ZL=F", "return_1m")
    myr_ret = _get_metric(metrics_df, "MYR=X", "return_1w")
    sgd_ret = _get_metric(metrics_df, "SGD=X", "return_1w")
    gold_ret = _get_metric(metrics_df, "GC=F", "return_1w")
    copper_ret = _get_metric(metrics_df, "HG=F", "return_1w")
    sp500_ret = _get_metric(metrics_df, "^GSPC", "return_1w")
    dxy_ret = _get_metric(metrics_df, "DX-Y.NYB", "return_1w")
    paragraphs = []
    paragraphs.append(
        f"This week, commodity markets were led by **{best_name}**, which gained {best_ret} "
        f"over the past five trading sessions. At the other end, **{worst_name}** was the "
        f"weakest performer, declining {worst_ret}. At a category level, **{best_cat}** showed "
        f"the strongest average weekly performance at {best_cat_ret}, while **{worst_cat}** "
        f"lagged with an average return of {worst_cat_ret}."
    )
    if brent_ret is not None or wti_ret is not None:
        direction = "higher" if (brent_ret or 0) >= 0 else "lower"
        paragraphs.append(
            f"In energy markets, Brent Crude moved {direction} by {format_pct(brent_ret)} over the week "
            f"(one-month return: {format_pct(brent_1m)}), while WTI Crude posted {format_pct(wti_ret)}. "
            f"Oil price direction continues to be shaped by global demand signals, OPEC+ supply decisions, "
            f"and broader macroeconomic sentiment."
        )
    if zl_ret is not None:
        direction = "rose" if zl_ret >= 0 else "fell"
        paragraphs.append(
            f"In agriculture, Soybean Oil — tracked here as a proxy for vegetable oil markets — "
            f"{direction} {format_pct(zl_ret)} this week (one-month: {format_pct(zl_1m)}). "
            f"Vegetable oil pricing tends to be sensitive to crushing margins, weather in growing regions, and biodiesel policy."
        )
    if gold_ret is not None and copper_ret is not None:
        if gold_ret > 0 and copper_ret < 0:
            rel = "Gold outperforming copper can signal a risk-off tilt in markets."
        elif copper_ret > 0 and gold_ret < 0:
            rel = "Copper outperforming gold typically suggests a risk-on environment."
        else:
            rel = "Both metals moved in the same direction this week."
        paragraphs.append(f"In metals, Gold was {format_pct(gold_ret)} on the week while Copper posted {format_pct(copper_ret)}. {rel}")
    fx_parts = []
    if myr_ret is not None:
        fx_parts.append(f"USD/MYR {format_pct(myr_ret)}")
    if sgd_ret is not None:
        fx_parts.append(f"USD/SGD {format_pct(sgd_ret)}")
    macro_parts = []
    if sp500_ret is not None:
        macro_parts.append(f"S&P 500 {format_pct(sp500_ret)}")
    if dxy_ret is not None:
        macro_parts.append(f"US Dollar Index {format_pct(dxy_ret)}")
    if fx_parts or macro_parts:
        combined = ". ".join(filter(None, [", ".join(fx_parts), ", ".join(macro_parts)]))
        paragraphs.append(f"On the macro and FX side: {combined}. A stronger US dollar typically weighs on dollar-denominated commodities.")
    paragraphs.append(
        "Looking ahead, market participants will be watching central bank commentary, US economic data releases, "
        "and geopolitical developments for directional cues."
    )
    note = "\n\n".join(paragraphs)
    note += "\n\n---\n*This note is generated for educational purposes and is not investment advice.*"
    return note
