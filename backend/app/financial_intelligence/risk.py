class RiskEngine:
    """
    Risk assessment and guardrails.
    """
    
    @staticmethod
    def calculate_max_drawdown(prices: list[float]) -> float:
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
    def check_risk_violation(current_drawdown: float, max_allowed_drawdown: float) -> bool:
        """
        Returns True if the risk constraint is violated.
        """
        return current_drawdown > max_allowed_drawdown
