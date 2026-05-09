import sqlite3

def create_db():
    con = sqlite3.connect("db/market.db")
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS candles_daily(
        ticker TEXT,
        date TEXT,
        open REAL,
        high REAL,
        low REAL,
        close REAL,
        adj_close REAL,
        volume INTEGER,
        PRIMARY KEY (ticker, date)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS indicators_daily(
        ticker TEXT,
        date TEXT,
        sma20 REAL,
        sma50 REAL,
        PRIMARY KEY (ticker, date)
    )
    """)

    con.commit()
    con.close()

if __name__ == "__main__":
    create_db()