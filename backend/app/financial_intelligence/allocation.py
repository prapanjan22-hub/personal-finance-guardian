class AssetAllocationEngine:
    """
    Rules-based asset allocation.
    """
    
    @staticmethod
    def get_allocation_strategy(risk_profile: str) -> dict:
        """
        Returns target allocation based on risk profile strings.
        """
        # Simple static mapping for now
        if risk_profile == "conservative":
            return {"equity": 0.3, "bonds": 0.6, "cash": 0.1}
        elif risk_profile == "moderate":
            return {"equity": 0.6, "bonds": 0.3, "cash": 0.1}
        elif risk_profile == "aggressive":
            return {"equity": 0.8, "bonds": 0.1, "cash": 0.1}
        else:
            # Default to conservative
            return {"equity": 0.3, "bonds": 0.6, "cash": 0.1}
