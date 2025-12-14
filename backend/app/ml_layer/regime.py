from typing import List
import numpy as np

class RegimeDetectionModel:
    """
    Probabilistic market regime detection using volatility and trend signals.
    """
    
    # Volatility thresholds (annualized)
    LOW_VOL_THRESHOLD = 0.15
    HIGH_VOL_THRESHOLD = 0.30
    
    @staticmethod
    def calculate_volatility(returns: List[float], annualize: bool = True) -> float:
        """
        Calculate volatility from returns.
        """
        if not returns or len(returns) < 2:
            return 0.0
        vol = np.std(returns)
        if annualize:
            vol *= np.sqrt(252)  # Annualize daily volatility
        return vol

    @staticmethod
    def calculate_trend(prices: List[float], window: int = 20) -> str:
        """
        Determine trend direction using simple moving average.
        """
        if len(prices) < window:
            return "neutral"
        
        sma = np.mean(prices[-window:])
        current_price = prices[-1]
        
        if current_price > sma * 1.02:
            return "up"
        elif current_price < sma * 0.98:
            return "down"
        return "neutral"
    
    def detect_regime(self, prices: List[float]) -> dict:
        """
        Detect market regime based on volatility and trend.
        
        Returns:
            dict with 'regime' and 'confidence' keys.
        """
        if len(prices) < 20:
            return {"regime": "unknown", "confidence": 0.0}
        
        # Calculate returns
        returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
        
        # Calculate metrics
        volatility = self.calculate_volatility(returns)
        trend = self.calculate_trend(prices)
        
        # Classify regime
        regime, confidence = self._classify_regime(volatility, trend)
        
        return {
            "regime": regime,
            "confidence": confidence,
            "volatility": volatility,
            "trend": trend
        }
    
    def _classify_regime(self, volatility: float, trend: str) -> tuple:
        """
        Classify regime based on volatility and trend.
        """
        if volatility > self.HIGH_VOL_THRESHOLD:
            if trend == "down":
                return ("crisis", 0.85)
            return ("bear", 0.70)
        elif volatility < self.LOW_VOL_THRESHOLD:
            if trend == "up":
                return ("bull", 0.80)
            return ("sideways", 0.65)
        else:
            if trend == "up":
                return ("bull", 0.60)
            elif trend == "down":
                return ("bear", 0.60)
            return ("sideways", 0.50)

