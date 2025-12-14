from sqlalchemy import Column, Integer, String, Float, DateTime, Date, ForeignKey, Index
from sqlalchemy.sql import func
from app.core.database import Base

class OHLCVData(Base):
    """
    Time series price data for assets.
    """
    __tablename__ = "ohlcv_data"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True, nullable=False)
    date = Column(Date, nullable=False)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('ix_ohlcv_ticker_date', 'ticker', 'date', unique=True),
    )


class FundamentalData(Base):
    """
    Company fundamental metrics.
    """
    __tablename__ = "fundamental_data"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True, nullable=False)
    report_date = Column(Date, nullable=False)
    
    # Key metrics
    market_cap = Column(Float)
    enterprise_value = Column(Float)
    pe_ratio = Column(Float)
    pb_ratio = Column(Float)
    revenue = Column(Float)
    net_income = Column(Float)
    free_cash_flow = Column(Float)
    total_debt = Column(Float)
    total_cash = Column(Float)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('ix_fundamental_ticker_date', 'ticker', 'report_date', unique=True),
    )
