# Commodity Tracker Dashboard

A Streamlit dashboard that tracks commodity markets and related FX/macro indicators, with multi-period return analysis, cross-asset comparison, and an auto-generated weekly market note.

Built with Python, Streamlit, pandas, plotly, and yfinance. No API keys required.

## Why I built this

I'm a Computer Engineering student with a long-standing interest in finance and physical commodities. I chose CE over CS because I wanted to work at the intersection of technology and real-world markets rather than in pure software. Energy and shipping were familiar topics growing up, which is why this project leans into oil, natural gas, and the FX pairs relevant to Southeast Asian trade flows. It's a way to connect the engineering skills I'm building with the markets I care about.

## Features

- Market data for commodities, FX, and macro benchmarks via yfinance, refreshed hourly
- Multi-period returns (1D, 1W, 1M, 3M, 6M) and 30-day annualized volatility
- 20- and 50-day moving averages with above/below signals
- Top movers ranking and category-level performance
- Cross-asset normalized comparison and daily-return correlation
- Auto-generated weekly market note
- Resilient data fetching — failed tickers are skipped, not fatal
- 1-hour data caching with a visible "last updated" timestamp

## Architecture

The app is organized into a thin UI layer (\`app.py\`) and a modular \`src/\` package, so the business logic is independent of Streamlit and can be tested on its own.

\`\`\`
app.py                  Streamlit UI — layout, tabs, widgets
src/
  config.py             Constants (asset list config, return windows)
  data_fetcher.py       yfinance fetching + caching + timestamp
  calculations.py       Returns, volatility, correlation, normalization
  charts.py             Plotly chart builders
  market_note.py        Template-based weekly note generator
  utils.py              Formatting helpers
data/
  assets.csv            Asset universe (symbol, name, category)
tests_calculations.py   Unit tests for the calculation logic
\`\`\`

**Data flow:** \`assets.csv\` defines the universe → \`data_fetcher\` pulls and caches prices → \`calculations\` derives metrics → \`charts\` and \`market_note\` render them → \`app.py\` assembles the UI.

A key design choice was keeping all numerical logic in \`calculations.py\` with no Streamlit dependencies, so it can be unit-tested in isolation.

## Testing

The calculation logic is covered by unit tests (pytest):

\`\`\`bash
pytest tests_calculations.py -v
\`\`\`

Tests verify return math, NaN handling, divide-by-zero protection, price normalization, and correlation — including edge cases like insufficient or missing data.

## Running locally

\`\`\`bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
streamlit run app.py
\`\`\`

Then open http://localhost:8501.

## Notes and limitations

- Data comes from Yahoo Finance via yfinance; some tickers may be temporarily unavailable, in which case they are skipped with a warning.
- Soybean Oil (ZL=F) is used as a proxy for palm oil-linked vegetable oil markets, since free palm oil futures data is limited.
- This is a portfolio and learning project, not investment advice.

## Possible next steps

- Brent–WTI spread tracker
- Rolling correlation over time
- Disk-persisted data cache
- Live deployment via Streamlit Community Cloud
