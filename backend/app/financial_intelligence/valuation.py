class ValuationEngine:
    """
    Deterministic valuation logic.
    """
    
    @staticmethod
    def calculate_dcf(cash_flows: list[float], discount_rate: float) -> float:
        """
        Simple Discounted Cash Flow calculation.
        """
        present_value = 0.0
        for i, cash_flow in enumerate(cash_flows):
            present_value += cash_flow / ((1 + discount_rate) ** (i + 1))
        return present_value

    @staticmethod
    def check_earnings_quality(net_income: float, operating_cash_flow: float) -> bool:
        """
        Simple rule: Earnings are high quality if Operating Cash Flow > Net Income.
        """
        return operating_cash_flow > net_income
