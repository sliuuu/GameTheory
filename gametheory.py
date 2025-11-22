import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf
import requests
import warnings
warnings.filterwarnings("ignore")

from data_cache import get_cache

# =====================================================
# GLOBAL GEOPOLITICAL MARKET GAME TRACKER (Nov 2025)
# Parties: Japan, China, USA, Germany, Taiwan (TSMC proxy)
# Assets tracked:
#   - Nikkei 225 (^N225)          → Japan
#   - Shanghai SSE Composite (000001.SS) → China
#   - S&P 500 (^GSPC)             → USA
#   - DAX (^GDAXI)                → Germany
#   - TAIEX (^TWII) & TSMC (2330.TW) → Taiwan
#   - USD/JPY, USD/CNY, Gold (GC=F), VIX (^VIX)
# =====================================================

class GeopoliticalMarketGame:
    def __init__(self):
        self.parties = ["Japan", "China", "USA", "Germany", "Taiwan"]
        self.tickers = {
            "Japan": "^N225",
            "China": "000001.SS",
            "USA": "^GSPC",
            "Germany": "^GDAXI",
            "Taiwan": "^TWII",
            "USDCNY": "CNY=X",
            "USDJPY": "JPY=X",
            "Gold": "GC=F",
            "VIX": "^VIX",
            # Additional major indices
            "SP500": "^GSPC",      # S&P 500 (explicit)
            "Nikkei225": "^N225",  # Nikkei 225 (explicit)
            "DAX": "^GDAXI",       # DAX (explicit)
            "TAIEX": "^TWII",      # TAIEX (explicit)
            "HangSeng": "^HSI"     # Hang Seng Index
        }
        self.actions = ["Hawkish Rhetoric / Sanctions", "De-escalate / Dialogue", "Economic Stimulus", "Military Posturing"]
        self.payoff_history = []
        self.current_date = datetime(2025, 11, 21)

    def fetch_real_time_data(self, days=30, use_cache=True, include_prices=False):
        end = self.current_date
        start = end - timedelta(days=days + 5)  # Add buffer for weekends/holidays
        data = {}
        prices = {} if include_prices else None
        cache = get_cache() if use_cache else None
        
        # For historical dates, ensure we're not requesting future dates
        now = datetime.now()
        if end > now:
            end_actual = now - timedelta(days=1)
            start_actual = end_actual - timedelta(days=days + 5)
        else:
            end_actual = end
            start_actual = start
        
        # Ensure start is before end
        if start_actual >= end_actual:
            start_actual = end_actual - timedelta(days=days + 5)
        
        for name, ticker in self.tickers.items():
            try:
                # Check cache first
                df = None
                if cache:
                    df = cache.get(ticker, start_actual, end_actual)
                
                if df is None or df.empty:
                    # Need to fetch from yfinance
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        # Convert to string format for yfinance
                        start_str = start_actual.strftime('%Y-%m-%d')
                        end_str = (end_actual + timedelta(days=1)).strftime('%Y-%m-%d')
                        
                        df = yf.download(ticker, start=start_str, end=end_str, 
                                       progress=False, auto_adjust=True, 
                                       timeout=10)
                    
                    # Cache the result
                    if cache and df is not None and not df.empty:
                        cache.put(ticker, start_actual, end_actual, df)
                    
                    if df is not None and not df.empty:
                        # Handle MultiIndex columns (yfinance sometimes returns these)
                        close_vals = pd.Series(dtype=float)
                        if isinstance(df.columns, pd.MultiIndex):
                            # MultiIndex: columns are (Price, Ticker) - e.g., ('Close', '^GSPC')
                            # Access Close column - it returns a DataFrame with ticker as column
                            try:
                                close_data = df['Close']
                                if isinstance(close_data, pd.DataFrame):
                                    # DataFrame with ticker columns - take first column
                                    close_vals = close_data.iloc[:, 0].dropna()
                                elif isinstance(close_data, pd.Series):
                                    # Single Series
                                    close_vals = close_data.dropna()
                            except (KeyError, IndexError):
                                # Try alternative access
                                if 'Close' in df.columns.get_level_values(0):
                                    close_vals = df.xs('Close', level=0, axis=1).iloc[:, 0].dropna()
                        elif 'Close' in df.columns:
                            close_vals = df['Close'].dropna()
                        
                        if len(close_vals) >= 2:
                            # Use first and last available values
                            start_val = float(close_vals.iloc[0])
                            end_val = float(close_vals.iloc[-1])
                            if start_val != 0 and not np.isnan(start_val) and not np.isnan(end_val):
                                data[name] = (end_val / start_val - 1)
                                if include_prices:
                                    prices[name] = end_val
                            else:
                                data[name] = 0.0
                                if include_prices:
                                    prices[name] = 0.0
                        elif len(close_vals) == 1:
                            # Only one data point, use it as baseline
                            data[name] = 0.0
                            if include_prices:
                                prices[name] = float(close_vals.iloc[0])
                        else:
                            data[name] = 0.0
                            if include_prices:
                                prices[name] = 0.0
                    else:
                        # No data fetched
                        data[name] = 0.0
                        if include_prices:
                            prices[name] = 0.0
                else:
                    # Use cached data to get current price
                    if include_prices and df is not None and not df.empty:
                        close_vals = pd.Series(dtype=float)
                        if isinstance(df.columns, pd.MultiIndex):
                            try:
                                close_data = df['Close']
                                if isinstance(close_data, pd.DataFrame):
                                    close_vals = close_data.iloc[:, 0].dropna()
                                elif isinstance(close_data, pd.Series):
                                    close_vals = close_data.dropna()
                            except (KeyError, IndexError):
                                if 'Close' in df.columns.get_level_values(0):
                                    close_vals = df.xs('Close', level=0, axis=1).iloc[:, 0].dropna()
                        elif 'Close' in df.columns:
                            close_vals = df['Close'].dropna()
                        
                        if len(close_vals) > 0:
                            prices[name] = float(close_vals.iloc[-1])
                        else:
                            prices[name] = 0.0
                    elif include_prices:
                        prices[name] = 0.0
                    data[name] = 0.0
            except Exception as e:
                # Log error but don't fail completely
                data[name] = 0.0
                if include_prices:
                    prices[name] = 0.0
        
        if include_prices:
            return data, prices
        return data

    def build_current_payoff_matrix(self):
        market = self.fetch_real_time_data(days=14)  # last 2 weeks most sensitive to rhetoric

        # Construct 5×4 payoff matrix (rows = parties, columns = actions)
        # Positive = benefits that country, negative = hurts
        P = np.zeros((5, 4))

        # Base market signals (higher return = better economy/security perception)
        returns = [
            market.get("Japan", 0.0),      # 0
            market.get("China", 0.0),      # 1
            market.get("USA", 0.0),        # 2
            market.get("Germany", 0.0),    # 3
            market.get("Taiwan", 0.0)      # 4
        ]

        # Normalize VIX: typical range 10-30, convert to -1 to +1 scale
        vix_raw = market.get("VIX", 0.0)
        vix = (vix_raw - 20.0) / 10.0  # Center at 20, scale by 10
        vix = np.clip(vix, -2.0, 2.0)  # Cap extreme values
        
        # Gold returns (already in percentage)
        gold = market.get("Gold", 0.0) * 10  # Amplify gold signal
        
        # Currency signals
        cny_strength = -market.get("USDCNY", 0.0) * 5  # CNY weakening helps Chinese exports
        jpy_strength = market.get("USDJPY", 0.0) * 5   # Yen weakening helps Japanese exporters
        
        # Calculate relative performance (how well country is doing vs others)
        avg_return = np.mean(returns)
        relative_performance = [r - avg_return for r in returns]

        # Country-specific base factors for differentiation
        country_factors = {
            "USA": {
                "hawk_bonus": 1.5,  # Strong military, can afford hawkish stance
                "deescalate_bonus": 0.3,  # Diplomatic leadership
                "stimulus_capacity": 2.0,  # Large economy, can stimulate
                "military_capacity": 1.8,  # Strong military
                "export_dependency": 0.15,  # Low export dependency
            },
            "China": {
                "hawk_bonus": 1.2,  # Territorial assertiveness
                "deescalate_bonus": 0.5,  # High export dependency favors stability
                "stimulus_capacity": 1.8,  # Large economy, state control
                "military_capacity": 1.3,  # Growing military
                "export_dependency": 0.7,  # High export dependency
            },
            "Japan": {
                "hawk_bonus": 0.3,  # Constitutional constraints
                "deescalate_bonus": 1.0,  # High export/energy dependency
                "stimulus_capacity": 1.5,  # Large economy
                "military_capacity": 0.2,  # Constitutionally limited
                "export_dependency": 0.65,  # High export dependency
            },
            "Germany": {
                "hawk_bonus": 0.4,  # Historical constraints
                "deescalate_bonus": 0.8,  # EU leadership, export dependency
                "stimulus_capacity": 1.3,  # EU constraints
                "military_capacity": 0.3,  # Historical constraints
                "export_dependency": 0.7,  # High export dependency
            },
            "Taiwan": {
                "hawk_bonus": 0.1,  # Small, vulnerable
                "deescalate_bonus": 1.5,  # Survival strategy
                "stimulus_capacity": 0.8,  # Smaller economy
                "military_capacity": 0.2,  # Limited military
                "export_dependency": 0.8,  # Very high export dependency
            }
        }

        for i, country in enumerate(self.parties):
            r = returns[i]
            rel_perf = relative_performance[i]
            factors = country_factors[country]
            
            # Action 0: Hawkish Rhetoric / Sanctions
            hawk_base = (
                2.0 * vix * factors["hawk_bonus"] +
                1.0 * gold * factors["hawk_bonus"] -
                0.8 * abs(r) * factors["export_dependency"] +  # Export-dependent countries hurt more
                0.3 * (avg_return - r) * factors["hawk_bonus"]  # If others struggling
            )
            if country == "China":
                hawk_base += 1.5 * cny_strength * factors["hawk_bonus"]
            if country == "Japan":
                hawk_base += 1.0 * jpy_strength * factors["hawk_bonus"]
            # USA gets bonus for alliance coordination
            if country == "USA":
                hawk_base += 0.5 * (vix > 0)  # Can coordinate with allies
            P[i, 0] = hawk_base

            # Action 1: De-escalate / Dialogue
            deescalate_base = (
                1.5 * r * (1 + factors["deescalate_bonus"]) -
                1.2 * vix * factors["export_dependency"] +  # Export-dependent benefit more from stability
                0.4 * rel_perf * factors["deescalate_bonus"] +
                0.5 * factors["deescalate_bonus"]  # Base preference for stability
            )
            # More attractive when volatility is high, especially for export-dependent
            if vix > 0.5:
                deescalate_base += 1.0 * factors["export_dependency"]
            # Taiwan strongly prefers de-escalation
            if country == "Taiwan":
                deescalate_base += 1.5  # Survival imperative
            P[i, 1] = deescalate_base

            # Action 2: Economic Stimulus
            stimulus_base = (
                2.5 * max(0, -r) * factors["stimulus_capacity"] +
                1.2 * r * factors["stimulus_capacity"] +
                0.5 * factors["stimulus_capacity"]
            )
            # More effective when relative performance is poor
            if rel_perf < -0.01:
                stimulus_base += 1.0 * factors["stimulus_capacity"]
            # Export-dependent countries benefit more from stimulus
            stimulus_base += 0.3 * factors["export_dependency"]
            P[i, 2] = stimulus_base

            # Action 3: Military Posturing
            military_base = (
                3.0 * vix * factors["military_capacity"] +
                2.0 * gold * factors["military_capacity"] -
                1.5 * abs(r) * factors["export_dependency"] -
                0.5 * r * factors["export_dependency"]
            )
            # Only attractive in extreme scenarios for countries with military capability
            if vix > 1.0 and gold > 0.02:
                military_base += 2.0 * factors["military_capacity"]
            else:
                military_base -= 1.5 * (1 - factors["military_capacity"])  # Heavy penalty for countries without capacity
            # USA gets coordination bonus
            if country == "USA" and vix > 0.5:
                military_base += 0.8  # Can coordinate with allies
            P[i, 3] = military_base

        # Add country-specific random noise to break ties (larger variance for differentiation)
        noise_scale = 0.15  # Increased from 0.01
        P += np.random.normal(0, noise_scale, P.shape)

        return P

    def solve_nash_equilibrium(self, payoff_matrix):
        # Improved regret-matching for 5-player 4-action game
        # Uses fictitious play with better expected payoff computation
        n_players = payoff_matrix.shape[0]
        n_actions = payoff_matrix.shape[1]
        
        # Initialize with slight bias toward actions with higher base payoffs
        strategies = np.zeros((n_players, n_actions))
        for player in range(n_players):
            base_payoffs = payoff_matrix[player, :]
            # Softmax initialization based on payoffs
            exp_payoffs = np.exp(2.0 * (base_payoffs - np.max(base_payoffs)))
            strategies[player] = exp_payoffs / exp_payoffs.sum()
        
        cumulative_strategy = strategies.copy()
        learning_rate = 0.1

        for iteration in range(5000):
            # Compute expected payoffs more accurately
            expected_payoffs = np.zeros((n_players, n_actions))
            
            for player in range(n_players):
                for action in range(n_actions):
                    # Expected payoff = base payoff + interaction effects
                    # Interaction: if others are also playing similar actions, adjust payoff
                    base_payoff = payoff_matrix[player, action]
                    
                    # Simple interaction model: if others play hawkish, hawkish becomes less effective
                    # This creates strategic interdependence
                    interaction_effect = 0.0
                    for other_player in range(n_players):
                        if other_player != player:
                            # Weight by opponent's strategy
                            for other_action in range(n_actions):
                                prob = strategies[other_player, other_action]
                                # If others play same action, reduce payoff (competition)
                                if other_action == action:
                                    interaction_effect -= 0.1 * prob
                                # If others play opposite (de-escalate vs hawk), adjust
                                elif (action == 0 and other_action == 1) or (action == 1 and other_action == 0):
                                    interaction_effect += 0.15 * prob
                    
                    expected_payoffs[player, action] = base_payoff + interaction_effect
            
            # Update strategies using fictitious play
            for player in range(n_players):
                # Best response with some exploration
                best_action = np.argmax(expected_payoffs[player])
                
                # Update strategy toward best response
                new_strategy = np.zeros(n_actions)
                new_strategy[best_action] = 1.0
                
                # Smooth update (fictitious play)
                strategies[player] = (1 - learning_rate) * strategies[player] + learning_rate * new_strategy
                
                # Add small exploration to avoid getting stuck
                strategies[player] = 0.95 * strategies[player] + 0.05 * np.ones(n_actions) / n_actions
                
                # Normalize
                strategies[player] = strategies[player] / strategies[player].sum()
                
                cumulative_strategy[player] += strategies[player]
            
            # Decay learning rate
            if iteration % 500 == 0:
                learning_rate *= 0.95

        # Return average strategy
        avg_strategy = cumulative_strategy / cumulative_strategy.sum(axis=1, keepdims=True)
        
        # Ensure minimum probability to avoid zero probabilities
        avg_strategy = np.maximum(avg_strategy, 0.01)
        avg_strategy = avg_strategy / avg_strategy.sum(axis=1, keepdims=True)
        
        return avg_strategy

    def predict_next_moves(self):
        P = self.build_current_payoff_matrix()
        strategies = self.solve_nash_equilibrium(P)

        print(f"=== GEOPOLITICAL MARKET GAME PREDICTIONS ===")
        print(f"Date: {self.current_date.strftime('%Y-%m-%d')}")
        print(f"Market context (14-day returns):")
        market = self.fetch_real_time_data(14)
        for k, v in market.items():
            print(f"  {k}: {v*100:+.2f}%")

        print("\nPredicted Mixed-Strategy Nash Equilibrium (next 1–3 weeks):")
        print("-" * 70)
        for i, country in enumerate(self.parties):
            probs = strategies[i]
            dominant = np.argmax(probs)
            print(f"{country:8s} → {self.actions[dominant]:25s} (probability {probs[dominant]:.1%})")
            print(f"          Full distribution: Hawk {probs[0]:.0%} | De-escalate {probs[1]:.0%} | Stimulus {probs[2]:.0%} | Military {probs[3]:.0%}")
            print()

        # Most likely global scenario
        scenario_counts = np.zeros(4)
        for i in range(5):
            scenario_counts[np.argmax(strategies[i])] += 1
        global_dominant = np.argmax(scenario_counts)
        print(f"⇒ MOST LIKELY NEAR-TERM SCENARIO: {self.actions[global_dominant].upper()}")
        return strategies

# =====================================================
# RUN THE MODEL (as of November 21, 2025)
# =====================================================

game = GeopoliticalMarketGame()
predictions = game.predict_next_moves()