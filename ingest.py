import yfinance as yf
import sqlite3
import pandas as pd

def fetch_and_store(ticker):
    print("📥 Downloading data...")

    df = yf.download(ticker, period="1y")

    if df.empty:
        raise ValueError("❌ No data fetched")

    # ✅ FIX 1: Flatten MultiIndex columns
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    # Reset index
    df.reset_index(inplace=True)

    # ✅ FIX 2: Convert all column names to string safely
    df.columns = [str(col).lower().replace(" ", "_") for col in df.columns]

    # Debug (optional)
    print("Columns:", df.columns)

    # Required columns
    required = ['date', 'open', 'high', 'low', 'close', 'volume']
    for col in required:
        if col not in df.columns:
            raise ValueError(f"❌ Missing column: {col}")

    # Handle adj_close safely
    if 'adj_close' not in df.columns:
        df['adj_close'] = df['close']

    # Format date
    df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')

    # Insert into DB
    con = sqlite3.connect("db/market.db")
    cur = con.cursor()

    for _, row in df.iterrows():
        cur.execute("""
        INSERT OR REPLACE INTO candles_daily
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ticker,
            row['date'],
            float(row['open']),
            float(row['high']),
            float(row['low']),
            float(row['close']),
            float(row['adj_close']),
            int(row['volume'])
        ))

    con.commit()
    con.close()

    print("✅ Data stored successfully")