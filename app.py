from fastapi import FastAPI
from src.ingest import fetch_and_store
from src.indicators import compute_indicators
from src.backtest import run_backtest

app = FastAPI()

@app.get("/")
def home():
    return {"message": "Stock Analyzer API Running"}

@app.post("/analyze/{ticker}")
def analyze(ticker: str):
    fetch_and_store(ticker)
    compute_indicators(ticker)
    result = run_backtest(ticker)

    return {
        "ticker": ticker,
        "analysis": result
    }