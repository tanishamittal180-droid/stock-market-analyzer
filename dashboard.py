import streamlit as st
import sqlite3
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
from users import users

# -----------------------------------
# 🎨 PAGE CONFIG
# -----------------------------------
st.set_page_config(
    page_title="Stock Analyzer Pro",
    layout="wide",
    page_icon="📈"
)

# -----------------------------------
# 🔐 LOGIN SYSTEM
# -----------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:

    st.title("🔐 Login - Stock Market Analyzer")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        if username in users and users[username]["password"] == password:

            st.session_state.logged_in = True
            st.session_state.username = username

            st.success("✅ Login Successful")
            st.rerun()

        else:
            st.error("❌ Invalid Credentials")

    st.stop()

# -----------------------------------
# 🎨 SIDEBAR
# -----------------------------------
st.sidebar.title("📊 Navigation")

st.sidebar.success(f"Welcome {st.session_state.username}")

if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

tickers_input = st.sidebar.text_input(
    "Enter Tickers",
    "AAPL,TSLA,NVDA"
)

tickers = [t.strip().upper() for t in tickers_input.split(",")]

date_range = st.sidebar.date_input(
    "Select Date Range",
    [datetime(2022,1,1), datetime.today()]
)

# -----------------------------------
# 🎯 HEADER
# -----------------------------------
st.title("📈 Stock Market Analyzer Pro")

st.markdown("""
### 🔥 Advanced FinTech Dashboard
Analyze stock performance, indicators, volatility, and trends.
""")

# -----------------------------------
# 📥 LOAD DATA
# -----------------------------------
@st.cache_data
def load_data(ticker):

    con = sqlite3.connect("db/market.db")

    df = pd.read_sql("""
        SELECT date, close
        FROM candles_daily
        WHERE ticker = ?
        ORDER BY date
    """, con, params=(ticker,))

    con.close()

    if df.empty:
        return df

    df['date'] = pd.to_datetime(df['date'])

    # ---------------------------
    # Moving Averages
    # ---------------------------
    df['sma20'] = df['close'].rolling(20).mean()
    df['sma50'] = df['close'].rolling(50).mean()

    # ---------------------------
    # RSI
    # ---------------------------
    delta = df['close'].diff()

    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    rs = gain.rolling(14).mean() / loss.rolling(14).mean()

    df['rsi'] = 100 - (100 / (1 + rs))

    # ---------------------------
    # MACD
    # ---------------------------
    ema12 = df['close'].ewm(span=12).mean()
    ema26 = df['close'].ewm(span=26).mean()

    df['macd'] = ema12 - ema26
    df['macd_signal'] = df['macd'].ewm(span=9).mean()

    # ---------------------------
    # Returns
    # ---------------------------
    df['returns'] = df['close'].pct_change()

    return df

# -----------------------------------
# 📦 LOAD STOCK DATA
# -----------------------------------
data = {}

for ticker in tickers:

    df = load_data(ticker)

    if not df.empty:

        df = df[
            (df['date'] >= pd.to_datetime(date_range[0])) &
            (df['date'] <= pd.to_datetime(date_range[1]))
        ]

        data[ticker] = df

# -----------------------------------
# 🚨 CHECK DATA
# -----------------------------------
if not data:
    st.error("❌ No data found. Run main.py first.")
    st.stop()

# -----------------------------------
# 📊 KPI SECTION
# -----------------------------------
st.subheader("📊 Market Overview")

cols = st.columns(len(data))

for i, (ticker, df) in enumerate(data.items()):

    with cols[i]:

        latest_price = round(df['close'].iloc[-1], 2)

        avg_return = round(df['returns'].mean() * 100, 2)

        volatility = round(df['returns'].std() * 100, 2)

        st.metric(
            label=f"{ticker} Price",
            value=f"${latest_price}"
        )

        st.metric(
            label="Avg Return",
            value=f"{avg_return}%"
        )

        st.metric(
            label="Volatility",
            value=f"{volatility}%"
        )

# -----------------------------------
# 📑 TABS
# -----------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Overview",
    "📊 Indicators",
    "📉 Comparison",
    "📋 Raw Data"
])

# ===================================
# 📈 OVERVIEW TAB
# ===================================
with tab1:

    st.subheader("📈 Stock Price Comparison")

    fig = go.Figure()

    colors = ["#00FFAA", "#FF4B4B", "#3399FF", "#FFD700"]

    for idx, (ticker, df) in enumerate(data.items()):

        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['close'],
            mode='lines',
            name=ticker,
            line=dict(
                width=3,
                color=colors[idx % len(colors)]
            )
        ))

    fig.update_layout(
        template="plotly_dark",
        height=500,
        title="Stock Price Trends"
    )

    st.plotly_chart(fig, width='stretch')

# ===================================
# 📊 INDICATORS TAB
# ===================================
with tab2:

    ticker = list(data.keys())[0]

    df = data[ticker]

    st.subheader(f"📊 Technical Indicators - {ticker}")

    # ---------------------------
    # SMA CHART
    # ---------------------------
    fig2 = go.Figure()

    fig2.add_trace(go.Scatter(
        x=df['date'],
        y=df['close'],
        name="Close",
        line=dict(color="cyan", width=3)
    ))

    fig2.add_trace(go.Scatter(
        x=df['date'],
        y=df['sma20'],
        name="SMA20",
        line=dict(color="orange")
    ))

    fig2.add_trace(go.Scatter(
        x=df['date'],
        y=df['sma50'],
        name="SMA50",
        line=dict(color="yellow")
    ))

    fig2.update_layout(
        template="plotly_dark",
        height=500
    )

    st.plotly_chart(fig2, width='stretch')

    # ---------------------------
    # RSI CHART
    # ---------------------------
    fig3 = go.Figure()

    fig3.add_trace(go.Scatter(
        x=df['date'],
        y=df['rsi'],
        name="RSI",
        line=dict(color="lime", width=3)
    ))

    fig3.add_hline(
        y=70,
        line_dash="dash",
        line_color="red"
    )

    fig3.add_hline(
        y=30,
        line_dash="dash",
        line_color="green"
    )

    fig3.update_layout(
        template="plotly_dark",
        height=400
    )

    st.plotly_chart(fig3, width='stretch')

    # ---------------------------
    # MACD CHART
    # ---------------------------
    fig4 = go.Figure()

    fig4.add_trace(go.Scatter(
        x=df['date'],
        y=df['macd'],
        name="MACD",
        line=dict(color="magenta")
    ))

    fig4.add_trace(go.Scatter(
        x=df['date'],
        y=df['macd_signal'],
        name="Signal",
        line=dict(color="yellow")
    ))

    fig4.update_layout(
        template="plotly_dark",
        height=400
    )

    st.plotly_chart(fig4, width='stretch')

# ===================================
# 📉 COMPARISON TAB
# ===================================
with tab3:

    st.subheader("📉 Returns Comparison")

    fig5 = go.Figure()

    for idx, (ticker, df) in enumerate(data.items()):

        fig5.add_trace(go.Scatter(
            x=df['date'],
            y=df['returns'],
            name=ticker,
            line=dict(
                width=2,
                color=colors[idx % len(colors)]
            )
        ))

    fig5.update_layout(
        template="plotly_dark",
        height=500
    )

    st.plotly_chart(fig5, width='stretch')

# ===================================
# 📋 RAW DATA TAB
# ===================================
with tab4:

    ticker = list(data.keys())[0]

    st.subheader(f"📋 Raw Data - {ticker}")

    st.dataframe(
        data[ticker].tail(100),
        width='stretch'
    )