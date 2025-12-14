from fastapi import APIRouter
import yfinance as yf

router = APIRouter()

@router.get("/indices")
def get_market_indices():
    """
    Get real-time market indices data.
    """
    indices = [
        {"symbol": "^GSPC", "name": "S&P 500"},
        {"symbol": "^DJI", "name": "DOW"},
        {"symbol": "^IXIC", "name": "NASDAQ"},
        {"symbol": "^NSEI", "name": "NIFTY"},
        {"symbol": "^BSESN", "name": "SENSEX"},
    ]
    
    result = []
    for idx in indices:
        try:
            ticker = yf.Ticker(idx["symbol"])
            hist = ticker.history(period="2d")
            
            if hist.empty or len(hist) < 2:
                continue
                
            current = float(hist["Close"].iloc[-1])
            previous = float(hist["Close"].iloc[-2])
            change = current - previous
            change_pct = (change / previous) * 100
            
            result.append({
                "name": idx["name"],
                "symbol": idx["symbol"],
                "value": round(current, 2),
                "change": round(change, 2),
                "change_percent": round(change_pct, 2),
                "is_positive": change >= 0
            })
        except Exception as e:
            print(f"Error fetching {idx['name']}: {e}")
            continue
    
    return {"indices": result}


@router.get("/stock/{ticker}")
def get_stock_data(ticker_symbol: str):
    """
    Get real-time stock data for a ticker.
    """
    try:
        ticker = yf.Ticker(ticker_symbol)
        hist = ticker.history(period="5d")
        
        if hist.empty or len(hist) < 2:
            return {"error": f"No data found for {ticker_symbol}"}
        
        current = float(hist["Close"].iloc[-1])
        previous = float(hist["Close"].iloc[-2])
        change = current - previous
        change_pct = (change / previous) * 100
        
        info = ticker.info
        
        return {
            "ticker": ticker_symbol,
            "price": round(current, 2),
            "change": round(change, 2),
            "change_percent": round(change_pct, 2),
            "is_positive": change >= 0,
            "high": round(float(hist["High"].iloc[-1]), 2),
            "low": round(float(hist["Low"].iloc[-1]), 2),
            "volume": int(hist["Volume"].iloc[-1]),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
        }
    except Exception as e:
        return {"error": str(e)}

