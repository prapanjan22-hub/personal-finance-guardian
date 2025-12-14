from typing import List

class ValuationEngine:
    """
    Deterministic valuation logic.
    """
    
    @staticmethod
    def calculate_dcf(
        cash_flows: List[float], 
        discount_rate: float, 
        terminal_growth_rate: float = 0.02
    ) -> float:
        """
        Calculates the Present Value of Projected Cash Flows + Terminal Value.
        
        Args:
            cash_flows: List of projected Free Cash Flows for N years.
            discount_rate: Weighted Average Cost of Capital (WACC).
            terminal_growth_rate: Long-term growth rate for terminal value (default 2%).
            
        Returns:
            float: Total Enterprise Value (PV of cash flows + PV of Terminal Value).
        """
        if not cash_flows:
            return 0.0
            
        present_value = 0.0
        
        # 1. PV of Explicit Period Cash Flows
        for i, cash_flow in enumerate(cash_flows):
            t = i + 1
            present_value += cash_flow / ((1 + discount_rate) ** t)
            
        # 2. Terminal Value (Gordon Growth Model) at end of year N
        last_cash_flow = cash_flows[-1]
        terminal_value = (last_cash_flow * (1 + terminal_growth_rate)) / (discount_rate - terminal_growth_rate)
        
        # 3. Discount Terminal Value to Present
        pv_terminal_value = terminal_value / ((1 + discount_rate) ** len(cash_flows))
        
        return present_value + pv_terminal_value

    @staticmethod
    def calculate_intrinsic_value(
        enterprise_value: float, 
        net_debt: float, 
        shares_outstanding: int
    ) -> float:
        """
        Calculates Equity Value per share.
        """
        if shares_outstanding == 0:
            return 0.0
        equity_value = enterprise_value - net_debt
        return equity_value / shares_outstanding

    @staticmethod
    def check_earnings_quality(net_income: float, operating_cash_flow: float) -> bool:
        """
        Simple rule: Earnings are high quality if Operating Cash Flow > Net Income.
        """
        return operating_cash_flow > net_income
