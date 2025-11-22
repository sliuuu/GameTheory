import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import yfinance as yf
import matplotlib.pyplot as plt
import warnings
import os
warnings.filterwarnings("ignore")

from gametheory import GeopoliticalMarketGame
from data_cache import get_cache
from utils.paths import get_output_dir

class GeopoliticalMarketGameBacktester(GeopoliticalMarketGame):
    def __init__(self, use_cache=True):
        super().__init__()
        self.backtest_results = []
        self.use_cache = use_cache
        self.cache = get_cache() if use_cache else None

    def run_backtest(self, start_date="2024-01-01", end_date="2025-11-21", freq="W-FRI", progress_callback=None):
        dates = pd.date_range(start=start_date, end=end_date, freq=freq)
        results = []
        total_dates = len(dates)

        print(f"Running historical backtest from {start_date} to {end_date} ({total_dates} weeks)")
        if self.use_cache and self.cache:
            stats = self.cache.get_stats()
            print(f"Using cache: {stats['total_entries']} entries ({stats['total_size_mb']:.2f} MB)")
        print()
        
        for idx, current_date in enumerate(dates, 1):
            # Update progress
            if progress_callback:
                progress = idx / total_dates
                progress_callback(progress, f"Processing {current_date.strftime('%Y-%m-%d')}", idx, total_dates)
            self.current_date = current_date
            try:
                P = self.build_current_payoff_matrix()
                strategies = self.solve_nash_equilibrium(P)
                
                # Determine dominant action per country
                dominant_actions = [self.actions[np.argmax(strat)] for strat in strategies]
                global_scenario = max(set(dominant_actions), key=dominant_actions.count)
                
                # Record actual next-week market outcome (risk-on / risk-off proxy)
                next_week = current_date + timedelta(days=7)
                # Don't try to fetch future data
                if next_week > datetime.now():
                    risk_off_actual = False
                else:
                    try:
                        with warnings.catch_warnings():
                            warnings.simplefilter("ignore")
                            end_date = min(next_week + timedelta(days=7), datetime.now() - timedelta(days=1))
                            
                            # Fetch VIX data (CBOE Volatility Index)
                            # Use wider date range to ensure data availability
                            vix_start = next_week - timedelta(days=2)  # Start 2 days earlier
                            vix_end = end_date + timedelta(days=2)     # End 2 days later
                            
                            # Check cache first
                            vix_df = None
                            if self.cache:
                                vix_df = self.cache.get("^VIX", vix_start, vix_end)
                            
                            if vix_df is None or vix_df.empty:
                                vix_start_str = vix_start.strftime('%Y-%m-%d')
                                vix_end_str = vix_end.strftime('%Y-%m-%d')
                                vix_df = yf.download("^VIX", start=vix_start_str, end=vix_end_str, 
                                                   progress=False, auto_adjust=True)
                                # Cache the result
                                if self.cache and vix_df is not None and not vix_df.empty:
                                    self.cache.put("^VIX", vix_start, vix_end, vix_df)
                            vix_values = []
                            if vix_df is not None and not vix_df.empty:
                                # Handle MultiIndex columns
                                if isinstance(vix_df.columns, pd.MultiIndex):
                                    if 'Close' in vix_df.columns.get_level_values(0):
                                        close_vals = vix_df['Close'].iloc[:, 0].dropna()
                                    else:
                                        close_vals = pd.Series(dtype=float)
                                elif 'Close' in vix_df.columns:
                                    close_vals = vix_df['Close'].dropna()
                                else:
                                    close_vals = pd.Series(dtype=float)
                                
                                # Filter to the actual week we care about
                                if len(close_vals) > 0:
                                    week_mask = (close_vals.index >= next_week) & (close_vals.index <= end_date)
                                    week_values = close_vals[week_mask] if week_mask.any() else close_vals
                                    vix_values = week_values.tolist() if len(week_values) > 0 else close_vals.tail(5).tolist()
                            
                            vix_next = float(np.mean(vix_values)) if len(vix_values) > 0 else 20.0
                            
                            # Fetch Nikkei data
                            # Check cache first
                            nikkei_df = None
                            if self.cache:
                                nikkei_df = self.cache.get("^N225", next_week, end_date)
                            
                            if nikkei_df is None or nikkei_df.empty:
                                nikkei_start_str = next_week.strftime('%Y-%m-%d')
                                nikkei_end_str = end_date.strftime('%Y-%m-%d')
                                nikkei_df = yf.download("^N225", start=nikkei_start_str, end=nikkei_end_str, 
                                                      progress=False, auto_adjust=True)
                                # Cache the result
                                if self.cache and nikkei_df is not None and not nikkei_df.empty:
                                    self.cache.put("^N225", next_week, end_date, nikkei_df)
                            nikkei_returns = []
                            if nikkei_df is not None and not nikkei_df.empty:
                                # Handle MultiIndex columns
                                if isinstance(nikkei_df.columns, pd.MultiIndex):
                                    if 'Close' in nikkei_df.columns.get_level_values(0):
                                        close_vals = nikkei_df['Close'].iloc[:, 0].dropna()
                                    else:
                                        close_vals = pd.Series(dtype=float)
                                elif 'Close' in nikkei_df.columns:
                                    close_vals = nikkei_df['Close'].dropna()
                                else:
                                    close_vals = pd.Series(dtype=float)
                                
                                if len(close_vals) > 1:
                                    pct_changes = close_vals.pct_change().dropna()
                                    nikkei_returns = pct_changes.tolist()
                            nikkei_next = float(np.mean(nikkei_returns)) if len(nikkei_returns) > 0 else 0.0
                            
                            # Fetch SSE data
                            # Check cache first
                            sse_df = None
                            if self.cache:
                                sse_df = self.cache.get("000001.SS", next_week, end_date)
                            
                            if sse_df is None or sse_df.empty:
                                sse_start_str = next_week.strftime('%Y-%m-%d')
                                sse_end_str = end_date.strftime('%Y-%m-%d')
                                sse_df = yf.download("000001.SS", start=sse_start_str, end=sse_end_str, 
                                                   progress=False, auto_adjust=True)
                                # Cache the result
                                if self.cache and sse_df is not None and not sse_df.empty:
                                    self.cache.put("000001.SS", next_week, end_date, sse_df)
                            sse_returns = []
                            if sse_df is not None and not sse_df.empty:
                                # Handle MultiIndex columns
                                if isinstance(sse_df.columns, pd.MultiIndex):
                                    if 'Close' in sse_df.columns.get_level_values(0):
                                        close_vals = sse_df['Close'].iloc[:, 0].dropna()
                                    else:
                                        close_vals = pd.Series(dtype=float)
                                elif 'Close' in sse_df.columns:
                                    close_vals = sse_df['Close'].dropna()
                                else:
                                    close_vals = pd.Series(dtype=float)
                                
                                if len(close_vals) > 1:
                                    pct_changes = close_vals.pct_change().dropna()
                                    sse_returns = pct_changes.tolist()
                            sse_next = float(np.mean(sse_returns)) if len(sse_returns) > 0 else 0.0
                            
                            # Risk-off criteria: high VIX OR significant market declines
                            # VIX > 20 indicates fear, or average Asian market decline > 0.5%
                            risk_off_actual = vix_next > 20.0 or (nikkei_next + sse_next) / 2 < -0.005
                    except Exception as e:
                        risk_off_actual = False

                result = {
                    'date': current_date,
                    'predicted_scenario': global_scenario,
                    'japan_action': dominant_actions[0],
                    'china_action': dominant_actions[1],
                    'usa_action': dominant_actions[2],
                    'germany_action': dominant_actions[3],
                    'taiwan_action': dominant_actions[4],
                    'actual_risk_off_next_week': risk_off_actual,
                    'hawk_dominant': global_scenario == "Hawkish Rhetoric / Sanctions"
                }
                results.append(result)
                
                status = '🟢 Correct' if (result['hawk_dominant'] == risk_off_actual) else '🔴 Wrong'
                print(f"[{idx}/{len(dates)}] {current_date.date()} | Predicted: {global_scenario:30s} | {status}")
            except Exception as e:
                print(f"[{idx}/{len(dates)}] {current_date.date()} | Data missing")

        self.backtest_results = pd.DataFrame(results)
        return self.backtest_results

    def backtest_summary(self):
        df = self.backtest_results
        if df.empty:
            print("No backtest data")
            return

        accuracy = (df['hawk_dominant'] == df['actual_risk_off_next_week']).mean()
        hawk_weeks_predicted = df['hawk_dominant'].sum()
        actual_risk_off_weeks = df['actual_risk_off_next_week'].sum()

        print("\n" + "="*60)
        print("HISTORICAL BACKTEST RESULTS (Jan 2024 – Nov 21 2025)")
        print("="*60)
        print(f"Total weeks tested           : {len(df)}")
        print(f"Overall prediction accuracy  : {accuracy:.1%}")
        print(f"Hawk-dominant weeks predicted: {hawk_weeks_predicted} ({hawk_weeks_predicted/len(df):.1%})")
        print(f"Actual risk-off weeks        : {actual_risk_off_weeks} ({actual_risk_off_weeks/len(df):.1%})")
        print(f"Hit rate when predicting Hawk: {(df[df['hawk_dominant']]['actual_risk_off_next_week'].mean()):.1%}")
        print(f"Hit rate when predicting Dove: {1 - df[~df['hawk_dominant']]['actual_risk_off_next_week'].mean():.1%}")

        # Key historical hits
        print("\nNotable correct predictions:")
        hits = df[(df['hawk_dominant'] == df['actual_risk_off_next_week']) & df['hawk_dominant']]
        for _, row in hits.tail(5).iterrows():
            print(f"  • {row['date'].date()}: Predicted HAWK → Risk-off confirmed")

        # Plot accuracy over time
        df['correct'] = df['hawk_dominant'] == df['actual_risk_off_next_week']
        plt.figure(figsize=(12,4))
        df.set_index('date')['correct'].rolling(10).mean().plot(title="10-Week Rolling Accuracy")
        plt.axhline(accuracy, color='green', linestyle='--', label=f'Overall {accuracy:.1%}')
        plt.legend()
        plt.ylabel("Accuracy")
        plt.tight_layout()
        output_dir = get_output_dir()
        output_file = output_dir / 'backtest_accuracy.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"\nPlot saved to: {output_file}")
        plt.close()

    def sensitivity_analysis(self, noise_levels=None, n_runs=200):
        """
        Monte-Carlo sensitivity analysis:
        - Adds Gaussian noise to the payoff matrix at different intensities
        - Re-solves Nash equilibrium many times
        - Measures how robust the current prediction is to market noise, model misspecification, etc.
        
        Parameters:
        -----------
        noise_levels : array-like, optional
            Array of noise standard deviations to test. If None, uses default range.
        n_runs : int, default=200
            Number of Monte Carlo runs per noise level
        """
        if noise_levels is None:
            # Default: test noise from 0 to 1.0 in 11 steps
            noise_levels = np.linspace(0.0, 1.0, 11)
        
        print(f"Running Monte-Carlo Sensitivity Analysis ({n_runs} runs per noise level)\n")
        base_payoff = self.build_current_payoff_matrix()
        
        # Calculate payoff magnitude for relative noise scaling
        payoff_std = np.std(base_payoff)
        payoff_mean = np.abs(np.mean(base_payoff))
        payoff_scale = max(payoff_std, payoff_mean, 1.0)  # Avoid division by zero
        
        results = []

        for noise_idx, noise in enumerate(noise_levels):
            hawk_japan = []
            hawk_china = []
            hawk_usa = []
            deesc_germany = []
            deesc_taiwan = []
            global_hawk = []
            global_deescalate = []

            for run in range(n_runs):
                try:
                    # Add calibrated Gaussian noise
                    # Scale noise relative to payoff magnitudes for more meaningful analysis
                    noise_scaled = noise * payoff_scale
                    noisy_payoff = base_payoff + np.random.normal(0, noise_scaled, base_payoff.shape)
                    
                    # Handle potential NaN or inf values
                    if np.any(np.isnan(noisy_payoff)) or np.any(np.isinf(noisy_payoff)):
                        noisy_payoff = np.nan_to_num(noisy_payoff, nan=0.0, posinf=10.0, neginf=-10.0)
                    
                    strategies = self.solve_nash_equilibrium(noisy_payoff)
                    dominant = np.argmax(strategies, axis=1)
                    
                    hawk_japan.append(dominant[0] == 0)
                    hawk_china.append(dominant[1] == 0)
                    hawk_usa.append(dominant[2] == 0)
                    deesc_germany.append(dominant[3] == 1)
                    deesc_taiwan.append(dominant[4] == 1)
                    global_hawk.append(np.sum(dominant == 0) >= 3)  # 3+ players hawkish
                    global_deescalate.append(np.sum(dominant == 1) >= 3)  # 3+ players de-escalate
                except Exception as e:
                    # If Nash solver fails, skip this run
                    continue

            if len(hawk_japan) > 0:  # Only add if we have valid results
                results.append({
                    'noise_level': noise,
                    'noise_scaled': noise * payoff_scale,
                    'Japan_Hawk': np.mean(hawk_japan),
                    'China_Hawk': np.mean(hawk_china),
                    'USA_Hawk': np.mean(hawk_usa),
                    'Germany_Deescalate': np.mean(deesc_germany),
                    'Taiwan_Deescalate': np.mean(deesc_taiwan),
                    'Global_Hawk_Scenario': np.mean(global_hawk),
                    'Global_Deescalate_Scenario': np.mean(global_deescalate),
                })
            
            # Progress indicator
            if (noise_idx + 1) % 3 == 0 or noise_idx == len(noise_levels) - 1:
                print(f"  Completed {noise_idx + 1}/{len(noise_levels)} noise levels...")

        if not results:
            print("Error: No valid results from sensitivity analysis")
            return None
            
        sens_df = pd.DataFrame(results)
        
        # Plot
        plt.figure(figsize=(12, 7))
        plt.plot(sens_df['noise_level'], sens_df['Japan_Hawk'], label='Japan Hawkish', marker='o', markersize=6)
        plt.plot(sens_df['noise_level'], sens_df['China_Hawk'], label='China Hawkish', marker='s', markersize=6)
        plt.plot(sens_df['noise_level'], sens_df['USA_Hawk'], label='USA Hawkish', marker='^', markersize=6)
        plt.plot(sens_df['noise_level'], sens_df['Germany_Deescalate'], label='Germany De-escalate', 
                linestyle='--', marker='d', markersize=6)
        plt.plot(sens_df['noise_level'], sens_df['Taiwan_Deescalate'], label='Taiwan De-escalate', 
                linestyle='--', marker='x', markersize=6)
        plt.plot(sens_df['noise_level'], sens_df['Global_Hawk_Scenario'], 
                label='Global Hawk Scenario (≥3 countries)', linewidth=3, color='red', marker='o')
        plt.plot(sens_df['noise_level'], sens_df['Global_Deescalate_Scenario'], 
                label='Global De-escalate Scenario (≥3 countries)', linewidth=3, color='green', marker='s')
        plt.axhline(0.5, color='gray', linestyle=':', alpha=0.6, label='50% threshold')
        plt.title(f'Sensitivity Analysis – Robustness of Predictions to Payoff Noise\n({self.current_date.strftime("%B %d, %Y")})')
        plt.xlabel('Noise Intensity (σ multiplier)')
        plt.ylabel('Probability of Predicted Strategy')
        plt.legend(loc='best', fontsize=9)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        # Save plot instead of showing (non-blocking)
        output_dir = get_output_dir()
        filename = output_dir / f'sensitivity_analysis_{self.current_date.strftime("%Y%m%d")}.png'
        plt.savefig(filename, dpi=150, bbox_inches='tight')
        print(f"\nPlot saved to: {filename}")
        plt.close()

        print("\n" + "="*70)
        print("SENSITIVITY ANALYSIS RESULTS")
        print("="*70)
        print(sens_df.round(3).to_string(index=False))
        print("\nInterpretation:")
        print("- Higher probabilities at low noise = robust predictions")
        print("- Rapid decay = sensitive to market data uncertainty")
        print("- Noise level represents standard deviation multiplier relative to payoff scale")
        
        return sens_df

# =====================================================
# RUN FULL BACKTEST + CURRENT PREDICTION
# =====================================================

if __name__ == "__main__":
    # Initialize backtester with caching enabled (default)
    backtester = GeopoliticalMarketGameBacktester(use_cache=True)
    
    print("Starting historical backtesting...")
    backtest_df = backtester.run_backtest()
    
    backtester.backtest_summary()
    
    # Show cache stats after backtest
    if backtester.cache:
        stats = backtester.cache.get_stats()
        print(f"\nCache stats: {stats['total_entries']} entries, {stats['total_size_mb']:.2f} MB")
        print(f"Cache location: {stats['cache_dir']}")
        print("(Subsequent runs will be much faster using cached data)")
    
    print("\n" + "="*60)
    print("LIVE PREDICTION AS OF NOVEMBER 21, 2025")
    print("="*60)
    backtester.predict_next_moves()