import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="AI ESG Proxy Dashboard", layout="wide")

st.title("🌱 AI-Based ESG Proxy Score Dashboard")
st.markdown("Market-Signal Driven Sustainability Intelligence")

# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.header("⚙️ Select Parameters")

company = st.sidebar.text_input("Enter Ticker", value="AAPL").upper()

analysis_depth = st.sidebar.selectbox(
    "Analysis Type",
    ["Standard", "Deep Analysis"]
)

period = st.sidebar.selectbox(
    "Historical Period",
    ["6mo", "1y", "2y"]
)

if company == "":
    st.warning("Please enter a ticker")
    st.stop()

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
# SAFE DATA LOAD
# -----------------------------
@st.cache_data
def load_data(ticker, period):
    try:
        data = yf.download(ticker, period=period, progress=False)
        if data is None or data.empty:
            return pd.DataFrame()
        return data
    except:
        return pd.DataFrame()

hist = load_data(company, period)

if hist.empty:
    st.error("Invalid ticker or no data")
    st.stop()

hist["returns"] = hist["Close"].pct_change()
hist.dropna(inplace=True)

# -----------------------------
# ESG SCORE
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
# ESG GAUGE
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
# PRICE TREND (STATIC CLEAN)
# -----------------------------
st.subheader("📈 Price Trend")

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=hist.index,
    y=hist["Close"],
    name="Price"
))

fig.add_trace(go.Scatter(
    x=hist.index,
    y=hist["Close"].rolling(20).mean(),
    name="MA20",
    line=dict(dash="dash")
))

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# COMPETITOR FIX (IMPORTANT)
# -----------------------------
sector = ticker_sector_map.get(company)

# fallback logic
if sector and sector in sector_competitors:
    comp_list = [c for c in sector_competitors[sector] if c != company]
else:
    # fallback: use all known tickers
    comp_list = list(ticker_sector_map.keys())
    comp_list = [c for c in comp_list if c != company]

# ALWAYS pick first valid competitor
competitor = comp_list[0] if comp_list else None

st.subheader("🏭 Sector Overview")
st.write("Sector:", sector if sector else "Unknown")
st.write("Competitor:", competitor)

# -----------------------------
# ESG COMPARISON
# -----------------------------
@st.cache_data
def calc_esg(ticker):
    try:
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
    except:
        return None

if competitor:
    comp_score = calc_esg(competitor)

    if comp_score:
        fig = go.Figure()
        fig.add_bar(x=[company], y=[esg_score], name=company)
        fig.add_bar(x=[competitor], y=[comp_score], name=competitor)
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

    hist["cum"] = (1 + hist["returns"]).cumprod()
    hist["peak"] = hist["cum"].cummax()
    hist["drawdown"] = (hist["cum"] - hist["peak"]) / hist["peak"]
    max_dd = hist["drawdown"].min()

    market = load_data("^GSPC", period)

    if not market.empty:
        market["returns"] = market["Close"].pct_change()
        df = pd.concat([hist["returns"], market["returns"]], axis=1).dropna()
        df.columns = ["stock", "market"]
        beta = df.cov().iloc[0,1] / df["market"].var()
    else:
        beta = np.nan

    col1, col2, col3 = st.columns(3)
    col1.metric("Max Drawdown", f"{round(max_dd*100,2)}%")
    col2.metric("Beta", "N/A" if np.isnan(beta) else round(beta,2))
    col3.metric("Sharpe", round(sharpe_ratio,2))

    # Rolling Sharpe
    hist["rolling_sharpe"] = (
        hist["returns"].rolling(30).mean() /
        hist["returns"].rolling(30).std()
    ) * np.sqrt(252)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist.index,
        y=hist["rolling_sharpe"],
        name="Rolling Sharpe"
    ))
    st.plotly_chart(fig, use_container_width=True)

    # Interpretation
    insight = ""

    if not np.isnan(beta):
        if beta > 1.2:
            insight += "High market sensitivity. "
        elif beta < 0.8:
            insight += "Defensive behavior. "

    if max_dd < -0.4:
        insight += "High downside risk. "
    else:
        insight += "Strong downside protection. "

    if sharpe_ratio > 1.5:
        insight += "Strong returns."
    else:
        insight += "Moderate performance."

    st.markdown(f"### 🧠 AI Interpretation\n{insight}")
