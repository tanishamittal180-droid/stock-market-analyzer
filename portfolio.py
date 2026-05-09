import sqlite3

def buy_stock(ticker, qty, price):
    con = sqlite3.connect("db/market.db")
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS portfolio(
        ticker TEXT,
        qty INTEGER,
        price REAL
    )
    """)

    cur.execute("INSERT INTO portfolio VALUES (?, ?, ?)", (ticker, qty, price))

    con.commit()
    con.close()

    print(f"✅ Bought {qty} shares of {ticker}")