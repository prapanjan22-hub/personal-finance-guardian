"""
Market Regime Detection Model.
Uses trained HMM when available, falls back to rule-based heuristics.
"""
import os
import pickle
from typing import List, Optional
import numpy as np


class RegimeDetectionModel:
    """
    Probabilistic market regime detection using:
    1. Trained Hidden Markov Model (if available)
    2. Volatility and trend heuristics (fallback)
    """
    
    # Volatility thresholds (annualized)
    LOW_VOL_THRESHOLD = 0.12
    MED_VOL_THRESHOLD = 0.20
    HIGH_VOL_THRESHOLD = 0.30
    
    def __init__(self):
        self.hmm_model = None
        self.regime_map = None
        self._load_trained_model()
    
    def _load_trained_model(self):
        """
        Load pre-trained HMM model if available.
        """
        model_path = os.path.join(
            os.path.dirname(__file__), "..", "models", "regime_hmm.pkl"
        )
        try:
            if os.path.exists(model_path):
                with open(model_path, "rb") as f:
                    model_data = pickle.load(f)
                self.hmm_model = model_data.get("model")
                self.regime_map = model_data.get("regime_map")
                print(f"Loaded trained HMM model (version: {model_data.get('version')})")
        except Exception as e:
            print(f"Could not load HMM model: {e}. Using rule-based detection.")
    
    def detect_regime(self, prices: List[float]) -> dict:
        """
        Detect market regime from price series.
        
        Returns:
            dict with 'regime', 'confidence', 'volatility', 'trend'
        """
        if len(prices) < 50:
            return {
                "regime": "unknown",
                "confidence": 0.0,
                "volatility": 0.0,
                "trend": "insufficient_data"
            }
        
        # Calculate features
        returns = np.diff(prices) / np.array(prices[:-1])
        volatility = self._calculate_volatility(returns)
        trend = self._calculate_trend(prices)
        momentum = self._calculate_momentum(prices)
        
        # Try HMM first
        if self.hmm_model is not None:
            try:
                regime, confidence = self._predict_with_hmm(returns, volatility, momentum)
            except Exception as e:
                print(f"HMM prediction failed: {e}. Using rules.")
                regime, confidence = self._classify_with_rules(volatility, trend, momentum)
        else:
            regime, confidence = self._classify_with_rules(volatility, trend, momentum)
        
        return {
            "regime": regime,
            "confidence": confidence,
            "volatility": volatility,
            "trend": trend
        }
    
    def _predict_with_hmm(self, returns: np.ndarray, volatility: float, momentum: float) -> tuple:
        """
        Predict regime using trained HMM.
        """
        # Prepare features (last observation)
        features = np.array([[returns[-1], volatility, momentum]])
        
        # Get state probabilities
        state = self.hmm_model.predict(features)[0]
        
        # Get probabilities for confidence
        log_probs = self.hmm_model.score_samples(features)[1]
        probs = np.exp(log_probs[0])
        confidence = float(np.max(probs))
        
        regime = self.regime_map.get(state, "unknown")
        
        # Upgrade to crisis if volatility is extreme
        if volatility > self.HIGH_VOL_THRESHOLD and regime == "bear":
            regime = "crisis"
            confidence = min(confidence + 0.1, 0.95)
        
        return regime, confidence
    
    def _classify_with_rules(self, volatility: float, trend: str, momentum: float) -> tuple:
        """
        Rule-based regime classification with improved accuracy.
        """
        # Crisis detection
        if volatility > self.HIGH_VOL_THRESHOLD:
            if trend == "down" or momentum < -0.1:
                return ("crisis", 0.88)
            return ("bear", 0.75)
        
        # Bear market
        if volatility > self.MED_VOL_THRESHOLD:
            if trend == "down":
                return ("bear", 0.72)
            elif trend == "up":
                return ("bull", 0.58)
            return ("sideways", 0.55)
        
        # Normal/Low volatility
        if volatility < self.LOW_VOL_THRESHOLD:
            if trend == "up" and momentum > 0.02:
                return ("bull", 0.82)
            elif trend == "down" and momentum < -0.02:
                return ("bear", 0.65)
            return ("sideways", 0.70)
        
        # Medium-low volatility
        if trend == "up" and momentum > 0:
            return ("bull", 0.68)
        elif trend == "down" and momentum < 0:
            return ("bear", 0.62)
        
        return ("sideways", 0.55)
    
    @staticmethod
    def _calculate_volatility(returns: np.ndarray, window: int = 20) -> float:
        """
        Calculate annualized rolling volatility.
        """
        if len(returns) < window:
            return float(np.std(returns) * np.sqrt(252))
        return float(np.std(returns[-window:]) * np.sqrt(252))
    
    @staticmethod
    def _calculate_trend(prices: List[float], window: int = 20) -> str:
        """
        Determine trend direction using SMA crossover.
        """
        if len(prices) < window:
            return "neutral"
        
        prices_arr = np.array(prices)
        sma = np.mean(prices_arr[-window:])
        current = prices_arr[-1]
        
        if current > sma * 1.015:
            return "up"
        elif current < sma * 0.985:
            return "down"
        return "neutral"
    
    @staticmethod
    def _calculate_momentum(prices: List[float], window: int = 50) -> float:
        """
        Calculate price momentum relative to SMA.
        """
        if len(prices) < window:
            return 0.0
        
        prices_arr = np.array(prices)
        sma = np.mean(prices_arr[-window:])
        return float((prices_arr[-1] - sma) / sma)


