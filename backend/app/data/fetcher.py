import yfinance as yf
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from app.data.models import OHLCVData, FundamentalData


class MarketDataFetcher:
    """
    Service for fetching market data from external sources.
    """
    
    @staticmethod
    def fetch_ohlcv(ticker: str, period: str = "1y") -> List[dict]:
        """
        Fetch OHLCV data using yfinance.
        
        Args:
            ticker: Stock symbol (e.g., 'AAPL')
            period: Data period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', 'max')
            
        Returns:
            List of OHLCV dictionaries.
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            
            data = []
            for date, row in hist.iterrows():
                data.append({
                    "ticker": ticker,
                    "date": date.date(),
                    "open": row["Open"],
                    "high": row["High"],
                    "low": row["Low"],
                    "close": row["Close"],
                    "volume": row["Volume"]
                })
            return data
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return []

    @staticmethod
    def fetch_fundamentals(ticker: str) -> Optional[dict]:
        """
        Fetch fundamental data using yfinance.
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            return {
                "ticker": ticker,
                "report_date": datetime.now().date(),
                "market_cap": info.get("marketCap"),
                "enterprise_value": info.get("enterpriseValue"),
                "pe_ratio": info.get("trailingPE"),
                "pb_ratio": info.get("priceToBook"),
                "revenue": info.get("totalRevenue"),
                "net_income": info.get("netIncomeToCommon"),
                "free_cash_flow": info.get("freeCashflow"),
                "total_debt": info.get("totalDebt"),
                "total_cash": info.get("totalCash")
            }
        except Exception as e:
            print(f"Error fetching fundamentals for {ticker}: {e}")
            return None


class MarketDataStore:
    """
    Service for storing market data to database.
    """
    
    @staticmethod
    def store_ohlcv(db: Session, data: List[dict]) -> int:
        """
        Store OHLCV data, updating existing records.
        Returns count of records stored.
        """
        count = 0
        for record in data:
            existing = db.query(OHLCVData).filter(
                OHLCVData.ticker == record["ticker"],
                OHLCVData.date == record["date"]
            ).first()
            
            if existing:
                for key, value in record.items():
                    setattr(existing, key, value)
            else:
                db.add(OHLCVData(**record))
                count += 1
        
        db.commit()
        return count

    @staticmethod
    def store_fundamentals(db: Session, data: dict) -> bool:
        """
        Store fundamental data.
        """
        if not data:
            return False
            
        existing = db.query(FundamentalData).filter(
            FundamentalData.ticker == data["ticker"],
            FundamentalData.report_date == data["report_date"]
        ).first()
        
        if existing:
            for key, value in data.items():
                setattr(existing, key, value)
        else:
            db.add(FundamentalData(**data))
        
        db.commit()
        return True
