import sys
import os

# Add backend to path so we can import app modules
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app.financial_intelligence.valuation import ValuationEngine
from app.financial_intelligence.risk import RiskEngine
from app.financial_intelligence.allocation import AssetAllocationEngine

def test_valuation():
    print("Testing Valuation...")
    # 5 years of $100 cash flow, 10% discount rate
    cash_flows = [100.0] * 5
    discount_rate = 0.10
    
    ev = ValuationEngine.calculate_dcf(cash_flows, discount_rate)
    print(f"DCF Enterprise Value: {ev}")
    
    # Intrinsic value
    share_price = ValuationEngine.calculate_intrinsic_value(ev, net_debt=100.0, shares_outstanding=10)
    print(f"Intrinsic Value per Share: {share_price}")
    
def test_risk():
    print("\nTesting Risk...")
    prices = [100, 105, 110, 90, 85, 95, 100]
    drawdown = RiskEngine.calculate_max_drawdown(prices)
    print(f"Max Drawdown: {drawdown} (Expected: ~0.227 from 110 to 85)")
    
    returns = [-0.05, 0.02, 0.03, -0.01, -0.02]
    var_95 = RiskEngine.calculate_var(returns, 0.95)
    print(f"VaR (95%): {var_95}")

def test_allocation():
    print("\nTesting Allocation...")
    strategy = AssetAllocationEngine.get_allocation_strategy("aggressive")
    print(f"Aggressive Strategy: {strategy}")
    
    current_value = 10000
    current_holdings = {"equity": 5000, "bonds": 4000, "cash": 1000}
    rebalance = AssetAllocationEngine.calculate_rebalancing_diff(current_value, current_holdings, strategy)
    print(f"Rebalance Actions: {rebalance}")

if __name__ == "__main__":
    test_valuation()
    test_risk()
    test_allocation()
