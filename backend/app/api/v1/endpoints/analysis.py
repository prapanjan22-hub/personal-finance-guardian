from fastapi import APIRouter, HTTPException
import yfinance as yf
from app.financial_intelligence.valuation import ValuationEngine
from app.financial_intelligence.risk import RiskEngine
from app.ml_layer.regime import RegimeDetectionModel

router = APIRouter()
regime_model = RegimeDetectionModel()

@router.post("/analyze/stock")
def analyze_stock(ticker: str):
    """
    Full analysis of a stock with real data validation.
    """
    # 1. Validate ticker exists
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="3mo")
        
        if hist.empty:
            raise HTTPException(
                status_code=404, 
                detail=f"Ticker '{ticker}' not found or has no data"
            )
        
        info = stock.info
        if not info or info.get("regularMarketPrice") is None:
            # Double check with history
            if len(hist) < 5:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Ticker '{ticker}' is invalid or has insufficient data"
                )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=404, 
            detail=f"Failed to fetch data for '{ticker}': {str(e)}"
        )
    
    # 2. Extract price data
    prices = hist["Close"].tolist()
    current_price = prices[-1] if prices else 0
    
    # 3. Calculate returns for risk analysis
    returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
    
    # 4. Run regime detection
    regime_result = regime_model.detect_regime(prices)
    
    # 5. Risk analysis
    max_drawdown = RiskEngine.calculate_max_drawdown(prices)
    var_95 = RiskEngine.calculate_var(returns, confidence_level=0.95)
    
    # 6. Risk check
    risk_violated = RiskEngine.check_risk_violation(
        current_drawdown=max_drawdown,
        max_allowed_drawdown=0.20,
        current_var=var_95,
        max_allowed_var=0.05
    )
    risk_violations = []
    if risk_violated:
        if max_drawdown > 0.20:
            risk_violations.append(f"Drawdown {max_drawdown*100:.1f}% exceeds 20% limit")
        if var_95 > 0.05:
            risk_violations.append(f"VaR {var_95*100:.1f}% exceeds 5% limit")
    
    # 7. Generate recommendation based on regime and risk
    recommendation = _generate_recommendation(
        regime=regime_result["regime"],
        regime_confidence=regime_result["confidence"],
        max_drawdown=max_drawdown,
        var_95=var_95,
        risk_violations=risk_violations
    )
    
    return {
        "ticker": ticker.upper(),
        "price": round(current_price, 2),
        "regime": regime_result["regime"],
        "regime_confidence": round(regime_result["confidence"] * 100, 1),
        "volatility": round(regime_result.get("volatility", 0) * 100, 2),
        "trend": regime_result.get("trend", "unknown"),
        "recommendation": recommendation["action"],
        "recommendation_reason": recommendation["reason"],
        "risk_check": "PASSED" if not risk_violations else "FAILED",
        "risk_violations": risk_violations,
        "metrics": {
            "max_drawdown": round(max_drawdown * 100, 2),
            "var_95": round(var_95 * 100, 2),
        }
    }


def _generate_recommendation(
    regime: str, 
    regime_confidence: float,
    max_drawdown: float,
    var_95: float,
    risk_violations: list
) -> dict:
    """
    Generate investment recommendation based on analysis.
    """
    # High risk = SELL/REDUCE
    if risk_violations:
        return {
            "action": "REDUCE",
            "reason": f"Risk limits exceeded: {', '.join(risk_violations)}"
        }
    
    # Regime-based recommendations
    if regime == "crisis":
        return {
            "action": "SELL",
            "reason": "Crisis regime detected - capital preservation priority"
        }
    elif regime == "bear" and regime_confidence > 0.65:
        return {
            "action": "REDUCE",
            "reason": f"Bear market with {regime_confidence*100:.0f}% confidence"
        }
    elif regime == "bull" and regime_confidence > 0.7:
        return {
            "action": "BUY",
            "reason": f"Bull market with {regime_confidence*100:.0f}% confidence"
        }
    elif regime == "sideways":
        return {
            "action": "HOLD",
            "reason": "Sideways market - wait for clearer signals"
        }
    else:
        return {
            "action": "HOLD",
            "reason": f"Uncertain regime ({regime}) - maintaining position"
        }

