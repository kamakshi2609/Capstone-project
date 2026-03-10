import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="AI ESG Proxy Dashboard", layout="wide")

st.title("🌱 AI-Based ESG Proxy Score Dashboard")
st.markdown("Market-Signal Driven Sustainability Intelligence")

# -----------------------------
# Sidebar Controls
# -----------------------------
st.sidebar.header("⚙️ Analysis Settings")

company = st.sidebar.text_input(
    "Enter Company Ticker",
    value="AAPL"
).upper()

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

# -----------------------------
# Sector Mapping (avoids rate limit)
# -----------------------------
ticker_sector_map = {
    "AAPL": "Technology",
    "MSFT": "Technology",
    "GOOGL": "Technology",
    "NVDA": "Technology",
    "AMZN": "Consumer Cyclical",
    "TSLA": "Consumer Cyclical",
    "JPM": "Financial Services",
    "BAC": "Financial Services",
    "WFC": "Financial Services",
    "XOM": "Energy",
    "CVX": "Energy",
    "JNJ": "Healthcare",
    "PFE": "Healthcare"
}

sector_competitors = {
    "Technology": ["AAPL", "MSFT", "GOOGL", "NVDA"],
    "Financial Services": ["JPM", "BAC", "WFC"],
    "Energy": ["XOM", "CVX"],
    "Consumer Cyclical": ["AMZN", "TSLA"],
    "Healthcare": ["JNJ", "PFE"]
}

# -----------------------------
# Cached Data Loader
# -----------------------------
@st.cache_data
def load_data(ticker, period):
    data = yf.download(ticker, period=period, progress=False)
    return data

if company:

    hist = load_data(company, period)

    if hist.empty:
        st.error("Invalid ticker or no data available.")
        st.stop()

    hist["returns"] = hist["Close"].pct_change()
    hist.dropna(inplace=True)

    # -----------------------------
    # ESG Proxy Calculation
    # -----------------------------
    volatility = hist["returns"].std() * np.sqrt(252)
    mean_return = hist["returns"].mean() * 252
    sharpe_ratio = mean_return / (volatility + 1e-6)

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
    # Price Chart
    # -----------------------------
    st.subheader("📈 Price Trend")

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
        name="Rolling Volatility"
    ))

    fig_vol.update_layout(hovermode="x unified")

    st.plotly_chart(fig_vol, use_container_width=True)

    # -----------------------------
    # Sector & Competitor
    # -----------------------------
    sector = ticker_sector_map.get(company, "Technology")

    competitor = None
    if sector in sector_competitors:
        possible = [c for c in sector_competitors[sector] if c != company]
        competitor = possible[0] if possible else None

    st.subheader("🏭 Sector Overview")
    st.write("Sector:", sector)
    st.write("Auto-Selected Competitor:", competitor)

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

        vol_s = 1 / (1 + vol * 8)
        ret_s = np.clip((mean_ret + 0.2) / 0.4, 0, 1)
        sharpe_s = np.clip((sharpe + 2) / 4, 0, 1)

        score = vol_s * 35 + ret_s * 30 + sharpe_s * 35
        return float(np.clip(score, 0, 100))

    if competitor:

        comp_score = calculate_esg(competitor)

        st.subheader("📊 ESG Comparison")

        fig_comp = go.Figure()
        fig_comp.add_trace(go.Bar(x=[company], y=[esg_score], name=company))
        fig_comp.add_trace(go.Bar(x=[competitor], y=[comp_score], name=competitor))

        fig_comp.update_layout(yaxis=dict(range=[0, 100]))

        st.plotly_chart(fig_comp, use_container_width=True)

    # -----------------------------
    # AI Sustainability Insight
    # -----------------------------
    st.subheader("🤖 AI Sustainability Insight")

    if volatility < 0.20:
        risk_label = "Low Risk"
    elif volatility < 0.35:
        risk_label = "Moderate Risk"
    else:
        risk_label = "High Risk"

    if esg_score >= 75:
        rating = "Sustainability Leader 🟢"
    elif esg_score >= 55:
        rating = "Sustainability Stable 🟡"
    else:
        rating = "Sustainability Risk 🔴"

    if sharpe_ratio > 1.5:
        performance_comment = "strong risk-adjusted efficiency"
    elif sharpe_ratio > 0.8:
        performance_comment = "moderate efficiency"
    else:
        performance_comment = "weak risk-adjusted structure"

    if risk_preference == "Conservative":
        alignment = "Suitable for conservative portfolios seeking stability." if volatility < 0.25 else "Volatility may exceed conservative tolerance."
    elif risk_preference == "Balanced":
        alignment = "Fits balanced portfolios blending growth and stability."
    else:
        alignment = "May appeal to aggressive investors targeting alpha."

    st.markdown(f"""
### 📊 Company: {company}

**Sector:** {sector}  
**ESG Proxy Score:** {round(esg_score,2)} / 100  
**Risk Category:** {risk_label}  
**Rating Tier:** {rating}

---

### 📈 Financial Signal Summary

• Annual Return: **{round(mean_return*100,2)}%**  
• Annual Volatility: **{round(volatility,3)}**  
• Sharpe Ratio: **{round(sharpe_ratio,2)}**

The company demonstrates **{performance_comment}**.

---

### 🎯 Investor Fit

{alignment}
""")

    if analysis_depth == "Deep Analysis":

        st.markdown(f"""
### 🔬 Deep Breakdown

**Stability Score:** {round(vol_score*100,1)}  
**Growth Score:** {round(return_score*100,1)}  
**Efficiency Score:** {round(sharpe_score*100,1)}

Lower volatility often reflects disciplined governance and institutional confidence.  
Higher Sharpe ratios indicate efficient capital allocation.

Overall, {company} positions itself as a **{rating}** entity within the {sector} sector.
""")
