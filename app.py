import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import random
import time

st.set_page_config(page_title="AI ESG Proxy Dashboard", layout="wide")

st.title("🌱 AI-Based ESG Proxy Score Dashboard")
st.markdown("Market-Signal Driven Sustainability Intelligence")

# -----------------------------
# Sidebar Controls
# -----------------------------
st.sidebar.header("⚙️ Analysis Settings")

company = st.sidebar.text_input("Enter Company Ticker", value="AAPL").upper()

risk_preference = st.sidebar.selectbox(
    "Investor Risk Profile",
    ["Conservative", "Balanced", "Aggressive"]
)

analysis_depth = st.sidebar.selectbox(
    "Insight Detail Level",
    ["Standard", "Deep Analysis"]
)

period = st.sidebar.selectbox(
    "Historical Period",
    ["6mo", "1y", "2y"]
)

auto_refresh = st.sidebar.checkbox("🔄 Live Price Update (5 sec)")

# -----------------------------
# Sector Mapping
# -----------------------------
ticker_sector_map = {
    "AAPL": "Technology", "MSFT": "Technology", "GOOGL": "Technology", "NVDA": "Technology",
    "AMZN": "Consumer Cyclical", "TSLA": "Consumer Cyclical",
    "JPM": "Financial Services", "BAC": "Financial Services", "WFC": "Financial Services",
    "XOM": "Energy", "CVX": "Energy",
    "JNJ": "Healthcare", "PFE": "Healthcare",

    # Indian stocks
    "RELIANCE.NS": "Energy",
    "TCS.NS": "Technology",
    "INFY.NS": "Technology",
    "HDFCBANK.NS": "Financial Services",
    "ICICIBANK.NS": "Financial Services",
    "SBIN.NS": "Financial Services",
    "ITC.NS": "Consumer Cyclical",
    "HINDUNILVR.NS": "Consumer Cyclical"
}

sector_competitors = {
    "Technology": ["AAPL", "MSFT", "GOOGL", "NVDA"],
    "Financial Services": ["JPM", "BAC", "WFC", "HDFCBANK.NS", "ICICIBANK.NS"],
    "Energy": ["XOM", "CVX", "RELIANCE.NS"],
    "Consumer Cyclical": ["AMZN", "TSLA", "ITC.NS"],
    "Healthcare": ["JNJ", "PFE"]
}

# -----------------------------
# Data Loader
# -----------------------------
@st.cache_data
def load_data(ticker, period):
    return yf.download(ticker, period=period, progress=False)

if company:

    hist = load_data(company, period)

    if hist.empty:
        st.error("Invalid ticker or no data available.")
        st.stop()

    hist["returns"] = hist["Close"].pct_change()
    hist.dropna(inplace=True)

    # -----------------------------
    # ESG Calculation
    # -----------------------------
    volatility = hist["returns"].std() * np.sqrt(252)
    mean_return = hist["returns"].mean() * 252
    sharpe_ratio = mean_return / (volatility + 1e-6)

    vol_score = 1 / (1 + volatility * 8)
    return_score = np.clip((mean_return + 0.2) / 0.4, 0, 1)
    sharpe_score = np.clip((sharpe_ratio + 2) / 4, 0, 1)

    esg_score = float(np.clip(
        vol_score * 35 + return_score * 30 + sharpe_score * 35, 0, 100
    ))

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
    # LIVE PRICE TREND
    # -----------------------------
    st.subheader("📈 Live Price Trend")

    placeholder = st.empty()

    def load_live_data(ticker):
        data = yf.download(ticker, period="1d", interval="1m", progress=False)
        data["MA50"] = data["Close"].rolling(50).mean()
        return data

    while True:

        live_data = load_live_data(company)

        if live_data.empty:
            st.warning("No live data available")
            break

        fig_price = go.Figure()

        fig_price.add_trace(go.Scatter(
            x=live_data.index,
            y=live_data["Close"],
            name="Close Price"
        ))

        fig_price.add_trace(go.Scatter(
            x=live_data.index,
            y=live_data["MA50"],
            name="MA50",
            line=dict(dash="dash")
        ))

        fig_price.update_layout(
            title=f"{company} Live Price",
            template="plotly_white"
        )

        placeholder.plotly_chart(fig_price, use_container_width=True)

        if not auto_refresh:
            break

        time.sleep(5)

    # -----------------------------
    # Rolling Volatility
    # -----------------------------
    st.subheader("⚠️ Rolling Volatility")

    hist["rolling_vol"] = hist["returns"].rolling(30).std() * np.sqrt(252)

    fig_vol = go.Figure()
    fig_vol.add_trace(go.Scatter(
        x=hist.index,
        y=hist["rolling_vol"],
        name="Volatility"
    ))

    st.plotly_chart(fig_vol, use_container_width=True)

    # -----------------------------
    # Sector + Competitor
    # -----------------------------
    sector = ticker_sector_map.get(company)

    if not sector:
        sector = "Financial Services" if company.endswith(".NS") else "Unknown"

    competitor = None
    if sector in sector_competitors:
        possible = [c for c in sector_competitors[sector] if c != company]
        if possible:
            competitor = random.choice(possible)

    st.subheader("🏭 Sector Overview")
    st.write("Sector:", sector)
    st.write(f"Competitor:", competitor)

    # -----------------------------
    # ESG Comparison
    # -----------------------------
    @st.cache_data
    def calculate_esg(ticker):
        h = yf.download(ticker, period=period, progress=False)
        if h.empty:
            return None

        h["returns"] = h["Close"].pct_change()
        h.dropna(inplace=True)

        vol = h["returns"].std() * np.sqrt(252)
        mean_ret = h["returns"].mean() * 252
        sharpe = mean_ret / (vol + 1e-6)

        return float(np.clip(
            (1/(1+vol*8))*35 +
            np.clip((mean_ret+0.2)/0.4,0,1)*30 +
            np.clip((sharpe+2)/4,0,1)*35, 0, 100
        ))

    if competitor:
        comp_score = calculate_esg(competitor)

        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(x=[company], y=[esg_score]))
        fig_comp.add_trace(go.Bar(x=[competitor], y=[comp_score]))

        st.plotly_chart(fig_comp, use_container_width=True)

    # -----------------------------
    # AI Insight
    # -----------------------------
    st.subheader("🤖 AI Insight")

    st.write(f"""
**ESG Score:** {round(esg_score,2)}  
**Volatility:** {round(volatility,3)}  
**Return:** {round(mean_return*100,2)}%  
**Sharpe:** {round(sharpe_ratio,2)}  
""")
