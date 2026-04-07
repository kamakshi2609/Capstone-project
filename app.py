# Streamlit ESG Proxy Dashboard
import streamlit as st
import yfinance as yf
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ------------------------------
# Page Config
# ------------------------------
st.set_page_config(page_title="🌱 ESG Proxy Dashboard", layout="wide", initial_sidebar_state="expanded")
st.title("🌱 ESG Proxy Dashboard")

# ------------------------------
# Sidebar Inputs
# ------------------------------
st.sidebar.header("Input Parameters")
company = st.sidebar.text_input("Enter Company Ticker", "AAPL").upper()
period = st.sidebar.selectbox("Select Period", ["6mo", "1y", "2y"])

# ------------------------------
# Fetch Data
# ------------------------------
@st.cache_data
def get_stock_data(ticker, period):
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)
    return hist, stock.info

hist, info = get_stock_data(company, period)

if hist.empty:
    st.error("Invalid ticker or no data available.")
    st.stop()

# ------------------------------
# Calculations
# ------------------------------
hist["returns"] = hist["Close"].pct_change()
hist.dropna(inplace=True)
hist["MA50"] = hist["Close"].rolling(50).mean()
hist["rolling_vol"] = hist["returns"].rolling(30).std() * np.sqrt(252)

# Annualized Metrics
volatility = hist["returns"].std() * np.sqrt(252)
mean_return = hist["returns"].mean() * 252
sharpe_ratio = mean_return / (volatility + 1e-6)

# Normalized ESG Scores
vol_score = 1 / (1 + volatility * 8)
return_score = np.clip((mean_return + 0.2) / 0.4, 0, 1)
sharpe_score = np.clip((sharpe_ratio + 2) / 4, 0, 1)

esg_score = vol_score*35 + return_score*30 + sharpe_score*35
esg_score = float(np.clip(esg_score, 0, 100))

# Risk & Rating
risk_label = "Low Risk" if volatility < 0.20 else ("Moderate Risk" if volatility < 0.35 else "High Risk")
rating = "Sustainability Leader 🟢" if esg_score >= 75 else ("Sustainability Stable 🟡" if esg_score >= 55 else "Sustainability Risk 🔴")

# ------------------------------
# Competitor Mapping
# ------------------------------
sector_competitors = {
    "Technology": ["AAPL", "MSFT", "GOOGL", "NVDA"],
    "Financial Services": ["JPM", "BAC"],
    "Energy": ["XOM", "CVX"]
}

sector = info.get("sector", "Unknown")
competitor = None
if sector in sector_competitors:
    possible = [c for c in sector_competitors[sector] if c != company]
    competitor = possible[0] if possible else None

# ESG Calculation Function
@st.cache_data
def calculate_esg(ticker, period="1y"):
    s = yf.Ticker(ticker)
    h = s.history(period=period)
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
    score = vol_s*35 + ret_s*30 + sharpe_s*35
    return float(np.clip(score, 0, 100))

if competitor:
    comp_score = calculate_esg(competitor, period)
    comparison_df = pd.DataFrame({
        "Company": [company, competitor],
        "ESG Proxy Score": [esg_score, comp_score]
    })

# ------------------------------
# Layout - Metrics
# ------------------------------
st.subheader(f"{company} ESG Insights")
col1, col2, col3, col4 = st.columns(4)
col1.metric("ESG Proxy Score", f"{round(esg_score,2)} / 100", "")
col2.metric("Annual Return", f"{round(mean_return*100,2)}%", "")
col3.metric("Annual Volatility", f"{round(volatility,3)}", "")
col4.metric("Sharpe Ratio", f"{round(sharpe_ratio,2)}", "")

st.markdown(f"**Risk Category:** {risk_label}  |  **Rating Tier:** {rating}")

# ------------------------------
# Price Chart
# ------------------------------
st.subheader("📈 Price Trend with 50-Day MA")
fig_price = go.Figure()
fig_price.add_trace(go.Scatter(x=hist.index, y=hist["Close"], mode='lines', name='Close Price', line=dict(color='blue')))
fig_price.add_trace(go.Scatter(x=hist.index, y=hist["MA50"], mode='lines', name='50-Day MA', line=dict(color='orange')))
fig_price.update_layout(height=400, xaxis_title="Date", yaxis_title="Price", template="plotly_dark")
st.plotly_chart(fig_price, use_container_width=True)

# ------------------------------
# Volatility Chart
# ------------------------------
st.subheader("📊 30-Day Rolling Volatility")
fig_vol = go.Figure()
fig_vol.add_trace(go.Scatter(x=hist.index, y=hist["rolling_vol"], mode='lines', name='Rolling Volatility', line=dict(color='red')))
fig_vol.update_layout(height=400, xaxis_title="Date", yaxis_title="Volatility", template="plotly_dark")
st.plotly_chart(fig_vol, use_container_width=True)

# ------------------------------
# Competitor Comparison
# ------------------------------
if competitor:
    st.subheader(f"⚖ ESG Score Comparison in {sector} Sector")
    st.dataframe(comparison_df)
    
    fig_comp = px.bar(comparison_df, x="Company", y="ESG Proxy Score", color="Company", text="ESG Proxy Score",
                      color_discrete_sequence=px.colors.qualitative.Set2)
    fig_comp.update_layout(yaxis=dict(range=[0,100]), template="plotly_dark", height=400)
    st.plotly_chart(fig_comp, use_container_width=True)
else:
    st.info("No competitor available for comparison.")

# ------------------------------
# AI Sustainability Insights
# ------------------------------
st.subheader("🤖 AI Sustainability Insight")
st.markdown(f"""
**Company:** {company}  
**Sector:** {sector}  
**ESG Proxy Score:** {round(esg_score,2)}  
**Risk Category:** {risk_label}  
**Rating Tier:** {rating}  

**Financial Signals:**  
- Annual Return: {round(mean_return*100,2)}%  
- Annual Volatility: {round(volatility,3)}  
- Sharpe Ratio: {round(sharpe_ratio,2)}  
""")

if sharpe_ratio > 1.5:
    st.success("Interpretation: Strong risk-adjusted performance.")
elif sharpe_ratio > 0.8:
    st.warning("Interpretation: Moderate efficiency.")
else:
    st.error("Interpretation: Weak risk-adjusted performance.")

st.markdown("""
Lower volatility may indicate disciplined governance.  
Higher Sharpe ratios reflect efficient capital allocation.
""")
