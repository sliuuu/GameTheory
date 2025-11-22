"""
Sensitivity Analysis Script for Geopolitical Market Game

This script demonstrates how to run sensitivity analysis on the current market predictions.
The sensitivity_analysis() method has been integrated into the GeopoliticalMarketGameBacktester class.

Usage:
    python3 sensitivity_analysis.py
"""

import numpy as np
import pandas as pd
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

from historical_backtesting import GeopoliticalMarketGameBacktester

# =====================================================
# RUN SENSITIVITY ANALYSIS
# =====================================================

if __name__ == "__main__":
    backtester = GeopoliticalMarketGameBacktester()
    
    print("="*70)
    print("SENSITIVITY ANALYSIS - ROBUSTNESS TESTING")
    print("="*70)
    print(f"Current date: {backtester.current_date.strftime('%Y-%m-%d')}\n")
    
    # Run sensitivity analysis with default parameters
    # You can customize:
    # - noise_levels: array of noise multipliers to test (default: 0.0 to 1.0 in 11 steps)
    # - n_runs: number of Monte Carlo runs per noise level (default: 200)
    
    print("Running sensitivity analysis...")
    print("This tests how robust predictions are to uncertainty in market data.\n")
    
    sens_df = backtester.sensitivity_analysis(n_runs=100)  # Reduced for faster execution
    
    if sens_df is not None and not sens_df.empty:
        print("\n" + "="*70)
        print("KEY INSIGHTS:")
        print("="*70)
        
        # Find robustness threshold (where probability drops below 50%)
        hawk_stable = sens_df[sens_df['Global_Hawk_Scenario'] > 0.5]
        deesc_stable = sens_df[sens_df['Global_Deescalate_Scenario'] > 0.5]
        
        if not hawk_stable.empty:
            max_noise_hawk = hawk_stable['noise_level'].max()
            print(f"✓ Global Hawk scenario remains likely (>50%) up to noise level: {max_noise_hawk:.2f}")
        else:
            print("✗ Global Hawk scenario is not robust (drops below 50% even at low noise)")
        
        if not deesc_stable.empty:
            max_noise_deesc = deesc_stable['noise_level'].max()
            print(f"✓ Global De-escalate scenario remains likely (>50%) up to noise level: {max_noise_deesc:.2f}")
        else:
            print("✗ Global De-escalate scenario is not robust (drops below 50% even at low noise)")
        
        # Baseline probabilities
        baseline = sens_df.iloc[0]
        print(f"\nBaseline predictions (zero noise):")
        print(f"  - Global Hawk probability: {baseline['Global_Hawk_Scenario']:.1%}")
        print(f"  - Global De-escalate probability: {baseline['Global_Deescalate_Scenario']:.1%}")
        
        # Most sensitive country
        country_sensitivities = {
            'Japan': sens_df['Japan_Hawk'].std(),
            'China': sens_df['China_Hawk'].std(),
            'USA': sens_df['USA_Hawk'].std(),
        }
        most_sensitive = max(country_sensitivities, key=country_sensitivities.get)
        print(f"\nMost sensitive country to noise: {most_sensitive} "
              f"(std dev: {country_sensitivities[most_sensitive]:.3f})")
        
        print("\n" + "="*70)
        print("RECOMMENDATION:")
        print("="*70)
        if baseline['Global_Hawk_Scenario'] > 0.5:
            if not hawk_stable.empty and max_noise_hawk > 0.3:
                print("✓ Prediction is ROBUST - High confidence in Hawk scenario")
            else:
                print("⚠ Prediction is SENSITIVE - Low confidence, monitor market data closely")
        elif baseline['Global_Deescalate_Scenario'] > 0.5:
            if not deesc_stable.empty and max_noise_deesc > 0.3:
                print("✓ Prediction is ROBUST - High confidence in De-escalate scenario")
            else:
                print("⚠ Prediction is SENSITIVE - Low confidence, monitor market data closely")
        else:
            print("⚠ Prediction is UNCERTAIN - Mixed signals, scenario unclear")
    else:
        print("Error: Sensitivity analysis failed to produce results")
