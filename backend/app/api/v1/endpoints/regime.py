from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.data.fetcher import MarketDataFetcher
from app.ml_layer.regime import RegimeDetectionModel

router = APIRouter()
regime_model = RegimeDetectionModel()

@router.get("/{ticker}")
def get_market_regime(ticker: str):
    """
    Get the current market regime for a given ticker.
    """
    # Fetch recent price data
    fetcher = MarketDataFetcher()
    data = fetcher.fetch_ohlcv(ticker, period="3mo")
    
    if not data:
        raise HTTPException(status_code=404, detail=f"No data found for {ticker}")
    
    # Extract closing prices
    prices = [d["close"] for d in data]
    
    # Detect regime
    result = regime_model.detect_regime(prices)
    result["ticker"] = ticker
    
    return result


@router.post("/ingest/{ticker}")
def ingest_ticker_data(ticker: str, db: Session = Depends(get_db)):
    """
    Manually trigger data ingestion for a ticker.
    """
    from app.data.fetcher import MarketDataFetcher, MarketDataStore
    
    fetcher = MarketDataFetcher()
    store = MarketDataStore()
    
    # Fetch and store OHLCV
    ohlcv_data = fetcher.fetch_ohlcv(ticker, period="1y")
    count = store.store_ohlcv(db, ohlcv_data)
    
    # Fetch and store fundamentals
    fundamentals = fetcher.fetch_fundamentals(ticker)
    store.store_fundamentals(db, fundamentals)
    
    return {
        "ticker": ticker,
        "ohlcv_records": count,
        "fundamentals_stored": fundamentals is not None
    }
