"""
Regime Detection Model Training Script.
Trains a Hidden Markov Model (HMM) on historical market data.
"""
import os
import pickle
import numpy as np
import yfinance as yf
from datetime import datetime, timedelta


def fetch_training_data(ticker: str = "SPY", years: int = 10):
    """
    Fetch historical data for model training.
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=years * 365)
    
    stock = yf.Ticker(ticker)
    hist = stock.history(start=start_date, end=end_date)
    
    return hist


def calculate_features(hist):
    """
    Calculate features for regime detection:
    - Returns
    - Volatility (rolling 20-day)
    - Momentum (price vs 50-day SMA)
    """
    prices = hist["Close"].values
    
    # Daily returns
    returns = np.diff(prices) / prices[:-1]
    
    # Rolling volatility (20-day, annualized)
    window = 20
    rolling_vol = []
    for i in range(window, len(returns)):
        vol = np.std(returns[i-window:i]) * np.sqrt(252)
        rolling_vol.append(vol)
    
    # Momentum (price relative to 50-day SMA)
    sma_window = 50
    momentum = []
    for i in range(sma_window, len(prices)):
        sma = np.mean(prices[i-sma_window:i])
        mom = (prices[i] - sma) / sma
        momentum.append(mom)
    
    # Align all features (use minimum length)
    min_len = min(len(rolling_vol), len(momentum))
    
    features = np.column_stack([
        returns[-min_len:],
        rolling_vol[-min_len:],
        momentum[-min_len:]
    ])
    
    return features


def train_hmm_model(features, n_states: int = 3, n_iter: int = 100):
    """
    Train a Gaussian HMM for regime detection.
    
    States:
    - 0: Low volatility (Bull/Sideways)
    - 1: Medium volatility (Transition)
    - 2: High volatility (Bear/Crisis)
    """
    try:
        from hmmlearn.hmm import GaussianHMM
    except ImportError:
        print("hmmlearn not installed. Using rule-based model.")
        return None
    
    model = GaussianHMM(
        n_components=n_states,
        covariance_type="full",
        n_iter=n_iter,
        random_state=42
    )
    
    model.fit(features)
    
    return model


def map_states_to_regimes(model, features):
    """
    Map HMM states to regime labels based on volatility characteristics.
    """
    states = model.predict(features)
    
    # Calculate average volatility for each state
    state_volatilities = {}
    for state in range(model.n_components):
        mask = states == state
        state_volatilities[state] = np.mean(features[mask, 1])  # volatility is feature index 1
    
    # Sort states by volatility
    sorted_states = sorted(state_volatilities.keys(), key=lambda x: state_volatilities[x])
    
    # Map to regimes
    regime_map = {
        sorted_states[0]: "bull",      # Lowest volatility
        sorted_states[1]: "sideways",  # Medium volatility
        sorted_states[2]: "bear"       # Highest volatility
    }
    
    return regime_map


def save_model(model, regime_map, model_path: str):
    """
    Save trained model and regime mapping.
    """
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    
    model_data = {
        "model": model,
        "regime_map": regime_map,
        "trained_at": datetime.now().isoformat(),
        "version": "1.0"
    }
    
    with open(model_path, "wb") as f:
        pickle.dump(model_data, f)
    
    print(f"Model saved to {model_path}")


def train_and_save():
    """
    Main training function.
    """
    print("Fetching training data (SPY, 10 years)...")
    hist = fetch_training_data("SPY", years=10)
    print(f"Fetched {len(hist)} data points")
    
    print("Calculating features...")
    features = calculate_features(hist)
    print(f"Feature shape: {features.shape}")
    
    print("Training HMM model...")
    model = train_hmm_model(features, n_states=3)
    
    if model is None:
        print("Training failed - using rule-based fallback")
        return
    
    print("Mapping states to regimes...")
    regime_map = map_states_to_regimes(model, features)
    print(f"Regime mapping: {regime_map}")
    
    # Save model
    model_path = os.path.join(os.path.dirname(__file__), "..", "models", "regime_hmm.pkl")
    save_model(model, regime_map, model_path)
    
    # Evaluate accuracy
    states = model.predict(features)
    print(f"\nModel Statistics:")
    print(f"  - Total samples: {len(states)}")
    for state, regime in regime_map.items():
        count = np.sum(states == state)
        pct = count / len(states) * 100
        print(f"  - {regime}: {count} samples ({pct:.1f}%)")
    
    print("\nTraining complete!")


if __name__ == "__main__":
    train_and_save()
