import sqlite3
import pandas as pd
import numpy as np

def run_backtest(ticker):
    con = sqlite3.connect("db/market.db")

    df = pd.read_sql("""
        SELECT c.date, c.close, i.sma20, i.sma50
        FROM candles_daily c
        JOIN indicators_daily i
        ON c.ticker=i.ticker AND c.date=i.date
        WHERE c.ticker=?
        ORDER BY c.date
    """, con, params=(ticker,))

    con.close()

    df.dropna(inplace=True)

    # Strategy: SMA crossover
    df['signal'] = (df['sma20'] > df['sma50']).astype(int)

    df['returns'] = df['close'].pct_change()
    df['strategy'] = df['signal'].shift(1) * df['returns']

    df.dropna(inplace=True)

    # Equity curve
    df['equity'] = (1 + df['strategy']).cumprod()

    # Metrics
    total_return = df['equity'].iloc[-1] - 1

    # Sharpe Ratio
    sharpe = np.sqrt(252) * df['strategy'].mean() / (df['strategy'].std() + 1e-9)

    # Max Drawdown
    peak = df['equity'].cummax()
    drawdown = (df['equity'] / peak - 1)
    max_dd = drawdown.min()

    trades = df['signal'].diff().abs().sum()

    return df, {
        "Total Return": round(total_return, 4),
        "Sharpe Ratio": round(sharpe, 2),
        "Max Drawdown": round(max_dd, 4),
        "Trades": int(trades)
    }