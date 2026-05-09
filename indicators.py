import sqlite3
import pandas as pd

def compute_indicators(ticker):
    con = sqlite3.connect("db/market.db")

    df = pd.read_sql(f"""
        SELECT date, close FROM candles_daily
        WHERE ticker='{ticker}'
        ORDER BY date
    """, con)

    # Moving averages
    df['sma20'] = df['close'].rolling(20).mean()
    df['sma50'] = df['close'].rolling(50).mean()

    # RSI (14)
    delta = df['close'].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss
    df['rsi'] = 100 - (100 / (1 + rs))

    # MACD
    ema12 = df['close'].ewm(span=12, adjust=False).mean()
    ema26 = df['close'].ewm(span=26, adjust=False).mean()

    df['macd'] = ema12 - ema26
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()

    df.dropna(inplace=True)

    # Save only SMA in DB (RSI & MACD for visualization)
    cur = con.cursor()

    for _, row in df.iterrows():
        cur.execute("""
        INSERT OR REPLACE INTO indicators_daily
        VALUES (?, ?, ?, ?)
        """, (
            ticker,
            row['date'],
            row['sma20'],
            row['sma50']
        ))

    con.commit()
    con.close()

    return df   # 🔥 return full df for charts