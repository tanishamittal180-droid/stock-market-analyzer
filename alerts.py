import sqlite3

def check_alert(ticker, threshold=30):
    con = sqlite3.connect("db/market.db")
    cur = con.cursor()

    row = cur.execute("""
        SELECT close FROM candles_daily
        WHERE ticker=?
        ORDER BY date DESC LIMIT 1
    """, (ticker,)).fetchone()

    if row and row[0] < threshold:
        print(f"🚨 ALERT: {ticker} below {threshold}")