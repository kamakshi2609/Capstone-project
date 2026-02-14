import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------

st.set_page_config(
    page_title="AI ESG Market Intelligence",
    layout="wide",
    page_icon="🌍"
)

st.markdown("""
<style>
.big-title {
    font-size:40px !important;
    font-weight:700;
}
.metric-card {
    background-color:#111827;
    padding:20px;
    border-radius:15px;
    text-align:center;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="big-title">🌍 AI-Driven ESG Market Intelligence Dashboard</p>', unsafe_allow_html=True)
st.write("Market-Based ESG Proxy Model using Quantitative Financial Signals")

# -------------------------------------------------
# USER INPUT
# -------------------------------------------------

company = st.text_input("Enter Company Ticker (e.g., AAPL, MSFT, TSLA, RELIANCE.NS)").upper()

# -------------------------------------------------
# AUTO COMPETITOR MAPPING
# -------------------------------------------------

sector_competitors = {
    "Technology": ["AAPL", "MSFT", "GOOGL", "NVDA"],
    "Financial Services": ["JPM", "BAC", "WFC"],
    "Energy": ["XOM", "CVX"],
    "Consumer Cyclical": ["AMZN", "TSLA"],
    "Healthcare": ["JNJ", "PFE"]
}

# -------------------------------------------------
# ESG FUNCTION
# -------------------------------------------------

def calculate_esg(ticker):
    stock = yf.Ticker(ticker)
    hist = stock.history(period="1y")

    if hist.empty:
        return None, None

    hist["returns"] = hist["Close"].pct_change()
    hist = hist.dropna()

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

    return esg_score, hist

# -------------------------------------------------
# ANALYSIS BUTTON
# -------------------------------------------------

if st.button("🚀 Analyze ESG Performance"):

    if company == "":
        st.warning("Please enter a valid ticker.")
    else:

        with st.spinner("Fetching real-time market data..."):

            try:
                stock = yf.Ticker(company)
                info = stock.info
                sector = info.get("sector", "Unknown")

                if sector in sector_competitors:
                    competitor_list = [c for c in sector_competitors[sector] if c != company]
                    competitor = competitor_list[0] if competitor_list else None
                else:
                    competitor = None

                company_esg, hist = calculate_esg(company)

                if company_esg is None:
                    st.error("Invalid ticker or no data available.")
                else:

                    # -------------------------------------------------
                    # ESG GAUGE
                    # -------------------------------------------------

                    st.markdown("## 🌍 ESG Proxy Score")

                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=company_esg,
                        title={'text': f"{company} ESG Score"},
                        gauge={
                            'axis': {'range': [0, 100]},
                            'steps': [
                                {'range': [0, 50], 'color': "#EF4444"},
                                {'range': [50, 75], 'color': "#FACC15"},
                                {'range': [75, 100], 'color': "#22C55E"}
                            ],
                        }
                    ))

                    st.plotly_chart(fig, use_container_width=True)

                    # -------------------------------------------------
                    # PRICE + MA CHART
                    # -------------------------------------------------

                    st.markdown("## 📈 Price Trend & Moving Average")

                    hist["MA50"] = hist["Close"].rolling(50).mean()

                    fig = go.Figure()

                    fig.add_trace(go.Scatter(
                        x=hist.index,
                        y=hist["Close"],
                        name="Close Price",
                        line=dict(width=2)
                    ))

                    fig.add_trace(go.Scatter(
                        x=hist.index,
                        y=hist["MA50"],
                        name="50-Day MA",
                        line=dict(dash="dash")
                    ))

                    fig.update_layout(hovermode="x unified")

                    st.plotly_chart(fig, use_container_width=True)

                    # -------------------------------------------------
                    # ROLLING VOLATILITY
                    # -------------------------------------------------

                    st.markdown("## ⚠ Risk Trend (Rolling Volatility)")

                    hist["rolling_vol"] = hist["returns"].rolling(30).std() * np.sqrt(252)

                    fig = go.Figure()

                    fig.add_trace(go.Scatter(
                        x=hist.index,
                        y=hist["rolling_vol"],
                        name="30-Day Rolling Volatility"
                    ))

                    fig.update_layout(hovermode="x unified")

                    st.plotly_chart(fig, use_container_width=True)

                    # -------------------------------------------------
                    # COMPETITOR COMPARISON
                    # -------------------------------------------------

                    if competitor:

                        competitor_esg, _ = calculate_esg(competitor)

                        st.markdown("## 🏆 ESG Benchmarking")

                        fig = go.Figure()

                        fig.add_trace(go.Bar(
                            x=[company],
                            y=[company_esg],
                            name=company
                        ))

                        fig.add_trace(go.Bar(
                            x=[competitor],
                            y=[competitor_esg],
                            name=competitor
                        ))

                        fig.update_layout(
                            title=f"{sector} Sector ESG Comparison",
                            yaxis=dict(range=[0,100])
                        )

                        st.plotly_chart(fig, use_container_width=True)

                        st.dataframe(pd.DataFrame({
                            "Company": [company, competitor],
                            "ESG Proxy Score": [round(company_esg,2), round(competitor_esg,2)]
                        }))

                    # -------------------------------------------------
                    # AI INSIGHT
                    # -------------------------------------------------

                    st.markdown("## 🤖 AI Sustainability Insight")

                    st.write(f"""
                    The ESG proxy score of **{round(company_esg,2)}** reflects 
                    market-based sustainability indicators derived from 
                    risk-adjusted performance and volatility stability.

                    Sector Detected: **{sector}**

                    Companies demonstrating lower volatility and stronger 
                    Sharpe-adjusted returns signal higher governance discipline 
                    and long-term financial resilience.
                    """)

            except:
                st.error("Data fetch failed. Try another ticker.")
