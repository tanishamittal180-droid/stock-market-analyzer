import matplotlib.pyplot as plt

# 📊 Price + MA + RSI + MACD
def plot_advanced(df, ticker):

    # Price + Moving Averages
    plt.figure(figsize=(10,5))
    plt.plot(df['date'], df['close'], label="Close")
    plt.plot(df['date'], df['sma20'], label="SMA20")
    plt.plot(df['date'], df['sma50'], label="SMA50")
    plt.legend()
    plt.title(f"{ticker} Price & Moving Averages")
    plt.xticks(rotation=45)
    plt.show()

    # RSI
    plt.figure(figsize=(10,4))
    plt.plot(df['date'], df['rsi'])
    plt.axhline(70, linestyle='--')
    plt.axhline(30, linestyle='--')
    plt.title("RSI Indicator")
    plt.xticks(rotation=45)
    plt.show()

    # MACD
    plt.figure(figsize=(10,4))
    plt.plot(df['date'], df['macd'], label="MACD")
    plt.plot(df['date'], df['macd_signal'], label="Signal")
    plt.legend()
    plt.title("MACD Indicator")
    plt.xticks(rotation=45)
    plt.show()


# 📈 Equity Curve (IMPORTANT FIX)
def plot_equity(df):

    plt.figure(figsize=(10,5))
    plt.plot(df['date'], df['equity'])
    plt.title("Equity Curve (Strategy Performance)")
    plt.xticks(rotation=45)
    plt.show()