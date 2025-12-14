from typing import List
import numpy as np

class RiskEngine:
    """
    Risk assessment and guardrails.
    """
    
    @staticmethod
    def calculate_max_drawdown(prices: List[float]) -> float:
        """
        Calculate Maximum Drawdown from a list of prices.
        """
        if not prices:
            return 0.0
            
        peak = prices[0]
        max_drawdown = 0.0
        
        for price in prices:
            if price > peak:
                peak = price
            drawdown = (peak - price) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
                
        return max_drawdown

    @staticmethod
    def calculate_var(
        returns: List[float], 
        confidence_level: float = 0.95
    ) -> float:
        """
        Calculate Value at Risk (VaR) using Historical Simulation method.
        
        Args:
            returns: List of historical percentage returns.
            confidence_level: The confidence level (default 0.95).
            
        Returns:
            float: The VaR value (positive number representing loss percentage).
        """
        if not returns:
            return 0.0
            
        # Sort returns
        sorted_returns = sorted(returns)
        
        # Calculate index for the quantile
        index = int((1 - confidence_level) * len(sorted_returns))
        
        # Return the value at that index (loss is negative, so flip sign if needed or return raw)
        # Usually VaR is expressed as a positive number representing potential loss
        var_value = -sorted_returns[index]
        return var_value if var_value > 0 else 0.0

    @staticmethod
    def check_risk_violation(
        current_drawdown: float, 
        max_allowed_drawdown: float,
        current_var: float = 0.0,
        max_allowed_var: float = 1.0
    ) -> bool:
        """
        Returns True if any risk constraint is violated.
        """
        if current_drawdown > max_allowed_drawdown:
            return True
        if current_var > max_allowed_var:
            return True
        return False
