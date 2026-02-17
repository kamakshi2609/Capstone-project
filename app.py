import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="ESG Proxy Score Dashboard", layout="wide")

st.title("🌱 AI-Based ESG Proxy Score Dashboard")
st.markdown("Risk-adjusted sustainability scoring using market signals")

# -----------------------------
# User Input
# -----------------------------
company = st.text_input(
    "Enter Company Ticker (e.g., RELIANCE.NS, TCS.NS, AAPL)",
    value="AAPL"
).upper()

if company:

    # -----------------------------
    # Fetch Data
    # -----------------------------
    stock = yf.Ticker(company)
    hist = stock.history(period="1y")

    if hist.empty:
        st.error("Invalid ticker or no data available.")
        st.stop()

    hist["returns"] = hist["Close"].pct_change()
    hist = hist.dropna()

    # -----------------------------
    # Feature Engineering
    # -----------------------------
    volatility = hist["returns"].std() * np.sqrt(252)
    mean_return = hist["returns"].mean() * 252
    sharpe_ratio = mean_return / (volatility + 1e-6)

    # Normalization
    vol_score = 1 / (1 + volatility * 8)
    return_score = np.clip((mean_return + 0.2) / 0.4, 0, 1)
    sharpe_score = np.clip((sharpe_ratio + 2) / 4, 0, 1)

    esg_score = (
        vol_score * 35 +
        return_score * 30 +
        sharpe_score * 35
    )

    esg_score = float(np.clip(esg_score, 0, 100))

    # -----------------------------
    # ESG Gauge
    # -----------------------------
    st.subheader("📊 ESG Proxy Score")

    gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=esg_score,
        title={'text': "ESG Proxy Score"},
        gauge={
            'axis': {'range': [0, 100]},
            'steps': [
                {'range': [0, 50], 'color': "red"},
                {'range': [50, 75], 'color': "yellow"},
                {'range': [75, 100], 'color': "green"}
            ],
        }
    ))

    st.plotly_chart(gauge, use_container_width=True)

    # -----------------------------
    # Price + Moving Average
    # -----------------------------
    st.subheader("📈 Price Trend with 50-Day Moving Average")

    hist["MA50"] = hist["Close"].rolling(50).mean()

    fig_price = go.Figure()
    fig_price.add_trace(go.Scatter(x=hist.index, y=hist["Close"], name="Close Price"))
    fig_price.add_trace(go.Scatter(x=hist.index, y=hist["MA50"], name="50-Day MA"))

    fig_price.update_layout(hovermode="x unified")
    st.plotly_chart(fig_price, use_container_width=True)

    # -----------------------------
    # Rolling Volatility
    # -----------------------------
    st.subheader("⚠️ Rolling Volatility (30-Day)")

    hist["rolling_vol"] = hist["returns"].rolling(30).std() * np.sqrt(252)

    fig_vol = go.Figure()
    fig_vol.add_trace(go.Scatter(
        x=hist.index,
        y=hist["rolling_vol"],
        name="30-Day Rolling Volatility"
    ))

    fig_vol.update_layout(hovermode="x unified")
    st.plotly_chart(fig_vol, use_container_width=True)

    # -----------------------------
    # Auto Competitor Detection
    # -----------------------------
    sector_competitors = {
        "Technology": ["AAPL", "MSFT", "GOOGL", "NVDA"],
        "Financial Services": ["JPM", "BAC", "WFC"],
        "Energy": ["XOM", "CVX"],
        "Consumer Cyclical": ["AMZN", "TSLA"],
        "Healthcare": ["JNJ", "PFE"]
    }

    info = stock.info
    sector = info.get("sector", None)

    competitor = None
    if sector in sector_competitors:
        possible = [c for c in sector_competitors[sector] if c != company]
        competitor = possible[0] if possible else None

    st.subheader("🏭 Sector Analysis")
    st.write("Detected Sector:", sector)
    st.write("Auto-Selected Competitor:", competitor)

    # -----------------------------
    # ESG Comparison
    # -----------------------------
    def calculate_esg(ticker):
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")

        if hist.empty:
            return None

        hist["returns"] = hist["Close"].pct_change()
        hist = hist.dropna()

        volatility = hist["returns"].std() * np.sqrt(252)
        mean_return = hist["returns"].mean() * 252
        sharpe_ratio = mean_return / (volatility + 1e-6)

        vol_score = 1 / (1 + volatility * 8)
        return_score = np.clip((mean_return + 0.2) / 0.4, 0, 1)
        sharpe_score = np.clip((sharpe_ratio + 2) / 4, 0, 1)

        esg = (
            vol_score * 35 +
            return_score * 30 +
            sharpe_score * 35
        )

        return float(np.clip(esg, 0, 100))

    if competitor:

        company_esg = calculate_esg(company)
        competitor_esg = calculate_esg(competitor)

        st.subheader("📊 ESG Comparison")

        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(x=[company], y=[company_esg], name=company))
        fig_comp.add_trace(go.Bar(x=[competitor], y=[competitor_esg], name=competitor))

        fig_comp.update_layout(
            yaxis=dict(range=[0, 100]),
            hovermode="x unified"
        )

        st.plotly_chart(fig_comp, use_container_width=True)

        comparison_df = pd.DataFrame({
            "Company": [company, competitor],
            "ESG Proxy Score": [
                round(company_esg, 2),
                round(competitor_esg, 2)
            ]
        })

        st.dataframe(comparison_df)

    # -----------------------------
    # AI Sustainability Insight
    # -----------------------------
    st.subheader("🤖 AI Sustainability Insight")

    st.markdown(f"""
**Annual Volatility:** {round(volatility,3)}  
**Annual Return:** {round(mean_return*100,2)}%  
**Sharpe Ratio:** {round(sharpe_ratio,2)}  

The ESG proxy score of **{round(esg_score,2)}** reflects  
risk-adjusted stability and market-based sustainability signals.  

Companies with lower volatility and higher Sharpe ratios  
indicate stronger governance discipline and long-term resilience.
""")
