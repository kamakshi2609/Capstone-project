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
# Sidebar
# -----------------------------
st.sidebar.header("⚙️ Select Parameters")

company = st.sidebar.text_input("Enter Ticker").upper()

analysis_depth = st.sidebar.selectbox(
    "Analysis Type",
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
    "JPM": "Financial Services", "BAC": "Financial Services",
    "XOM": "Energy", "CVX": "Energy",
    "JNJ": "Healthcare", "PFE": "Healthcare",

    "RELIANCE.NS": "Energy",
    "TCS.NS": "Technology",
    "INFY.NS": "Technology",
    "HDFCBANK.NS": "Financial Services",
    "ICICIBANK.NS": "Financial Services"
}

sector_competitors = {
    "Technology": ["AAPL", "MSFT", "GOOGL", "NVDA"],
    "Financial Services": ["JPM", "BAC", "HDFCBANK.NS"],
    "Energy": ["XOM", "CVX", "RELIANCE.NS"],
    "Consumer Cyclical": ["AMZN", "TSLA"],
    "Healthcare": ["JNJ", "PFE"]
}

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data(ticker, period):
    return yf.download(ticker, period=period, progress=False)

hist = load_data(company, period)

if hist.empty:
    st.error("Invalid ticker")
    st.stop()

hist["returns"] = hist["Close"].pct_change()
hist.dropna(inplace=True)

# -----------------------------
# ESG Score
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
    title={'text': "ESG Score"},
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
    live = load_live_data(company)

    if live.empty:
        st.warning("No live data")
        break

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=live.index,
        y=live["Close"],
        name="Price"
    ))

    fig.add_trace(go.Scatter(
        x=live.index,
        y=live["MA50"],
        name="MA50",
        line=dict(dash="dash")
    ))

    placeholder.plotly_chart(fig, use_container_width=True)

    if not auto_refresh:
        break

    time.sleep(5)

# -----------------------------
# Sector + Competitor
# -----------------------------
sector = ticker_sector_map.get(company, "Unknown")

competitor = None
if sector in sector_competitors:
    comp_list = [c for c in sector_competitors[sector] if c != company]
    if comp_list:
        competitor = random.choice(comp_list)

st.subheader("🏭 Sector Overview")
st.write("Sector:", sector)
st.write("Competitor:", competitor)

# -----------------------------
# ESG Comparison
# -----------------------------
@st.cache_data
def calc_esg(ticker):
    h = yf.download(ticker, period=period, progress=False)
    if h.empty:
        return None
    h["returns"] = h["Close"].pct_change()
    h.dropna(inplace=True)
    vol = h["returns"].std() * np.sqrt(252)
    mean = h["returns"].mean() * 252
    sharpe = mean / (vol + 1e-6)

    return float(np.clip(
        (1/(1+vol*8))*35 +
        np.clip((mean+0.2)/0.4,0,1)*30 +
        np.clip((sharpe+2)/4,0,1)*35, 0, 100
    ))

if competitor:
    comp_score = calc_esg(competitor)

    fig = go.Figure()
    fig.add_bar(x=[company], y=[esg_score])
    fig.add_bar(x=[competitor], y=[comp_score])

    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# AI INSIGHT
# -----------------------------
st.subheader("🤖 AI Insight")

st.write(f"""
ESG Score: {round(esg_score,2)}  
Volatility: {round(volatility,3)}  
Return: {round(mean_return*100,2)}%  
Sharpe: {round(sharpe_ratio,2)}
""")

# -----------------------------
# DEEP ANALYSIS
# -----------------------------
if analysis_depth == "Deep Analysis":

    st.subheader("🧠 Deep Analysis")

    # Drawdown
    hist["cum"] = (1 + hist["returns"]).cumprod()
    hist["peak"] = hist["cum"].cummax()
    hist["drawdown"] = (hist["cum"] - hist["peak"]) / hist["peak"]
    max_dd = hist["drawdown"].min()

    # Beta
    market = yf.download("^GSPC", period=period, progress=False)
    market["returns"] = market["Close"].pct_change()

    df = pd.concat([hist["returns"], market["returns"]], axis=1).dropna()
    df.columns = ["stock", "market"]

    beta = df.cov().iloc[0,1] / df["market"].var()

    # Rolling Sharpe
    hist["rolling_sharpe"] = (
        hist["returns"].rolling(30).mean() /
        hist["returns"].rolling(30).std()
    ) * np.sqrt(252)

    col1, col2, col3 = st.columns(3)
    col1.metric("Max Drawdown", f"{round(max_dd*100,2)}%")
    col2.metric("Beta", round(beta,2))
    col3.metric("Sharpe", round(sharpe_ratio,2))

    # Chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist.index,
        y=hist["rolling_sharpe"],
        name="Rolling Sharpe"
    ))
    st.plotly_chart(fig, use_container_width=True)

    # AI Interpretation
    insight = ""

    if beta > 1.2:
        insight += "High market sensitivity. "
    elif beta < 0.8:
        insight += "Defensive stock behavior. "

    if max_dd < -0.4:
        insight += "High downside risk historically. "
    else:
        insight += "Strong downside protection. "

    if sharpe_ratio > 1.5:
        insight += "Strong risk-adjusted returns."
    else:
        insight += "Moderate performance."

    st.markdown(f"### 🧠 AI Interpretation\n{insight}")
