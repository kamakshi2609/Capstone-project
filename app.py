import streamlit as st
import yfinance as yf
import pandas as pd
import time
import plotly.graph_objects as go

st.set_page_config(page_title="Live Stock Tracker", layout="wide")

st.title("📈 Live Stock Price Trend")

# User input
ticker = st.text_input("Enter Stock Symbol", "AAPL")

# Refresh interval
refresh_rate = st.slider("Refresh interval (seconds)", 5, 60, 10)

# Placeholder for chart
chart_placeholder = st.empty()

while True:
    try:
        # Fetch data
        data = yf.download(ticker, period="3mo", interval="1d")

        if data.empty:
            st.warning("No data found. Check ticker symbol.")
            break

        # Moving Average
        data["MA50"] = data["Close"].rolling(50).mean()

        # Plotly chart (interactive + smooth)
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["Close"],
            mode='lines',
            name='Close Price'
        ))

        fig.add_trace(go.Scatter(
            x=data.index,
            y=data["MA50"],
            mode='lines',
            name='50-Day MA'
        ))

        fig.update_layout(
            title=f"{ticker} Price Trend (Live)",
            xaxis_title="Date",
            yaxis_title="Price",
            template="plotly_white"
        )

        chart_placeholder.plotly_chart(fig, use_container_width=True)

        time.sleep(refresh_rate)
        st.rerun()

    except Exception as e:
        st.error(f"Error: {e}")
        break
