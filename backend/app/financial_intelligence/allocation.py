from typing import Dict

class AssetAllocationEngine:
    """
    Rules-based asset allocation.
    """
    
    # Static definitions of model portfolios
    PORTFOLIOS = {
        "conservative": {"equity": 0.3, "bonds": 0.6, "cash": 0.1},
        "moderate": {"equity": 0.6, "bonds": 0.3, "cash": 0.1},
        "aggressive": {"equity": 0.8, "bonds": 0.1, "cash": 0.1},
        "growth": {"equity": 0.9, "bonds": 0.05, "cash": 0.05}
    }

    @staticmethod
    def get_allocation_strategy(risk_profile: str) -> Dict[str, float]:
        """
        Returns target allocation based on risk profile strings.
        """
        return AssetAllocationEngine.PORTFOLIOS.get(risk_profile.lower(), AssetAllocationEngine.PORTFOLIOS["conservative"])

    @staticmethod
    def calculate_rebalancing_diff(
        current_portfolio_value: float,
        current_holdings: Dict[str, float],
        target_allocation: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculates the value to buy (positive) or sell (negative) for each asset class
        to return to target allocation.
        """
        rebalancing_actions = {}
        for asset_class, target_weight in target_allocation.items():
            current_value = current_holdings.get(asset_class, 0.0)
            target_value = current_portfolio_value * target_weight
            diff = target_value - current_value
            rebalancing_actions[asset_class] = diff
            
        return rebalancing_actions
