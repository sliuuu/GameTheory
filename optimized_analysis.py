"""
Demo script for Optimized Geopolitical Market Game Tracker
Shows country-specific analysis with different equilibrium types
"""

from optimized_gametheory import OptimizedGeopoliticalGame, EquilibriumType
from datetime import datetime
import numpy as np


def main():
    print("=" * 80)
    print("OPTIMIZED GEOPOLITICAL MARKET GAME TRACKER")
    print("Country-Specific Analysis with Constraints and Alliances")
    print("=" * 80)
    print()
    
    game = OptimizedGeopoliticalGame()
    game.current_date = datetime.now()
    
    # Build payoff matrix
    P = game.build_current_payoff_matrix()
    
    print("PAYOFF MATRIX (Country x Action):")
    print("-" * 80)
    print(f"{'Country':<10} {'Hawkish':>12} {'De-escalate':>14} {'Stimulus':>12} {'Military':>12}")
    print("-" * 80)
    for i, country in enumerate(game.parties):
        print(f"{country:<10}", end="")
        for j in range(4):
            print(f"{P[i, j]:>12.2f}", end="")
        print()
    print()
    
    # Analyze with different equilibrium types
    for eq_type in [EquilibriumType.NASH, EquilibriumType.BAYESIAN, EquilibriumType.REPEATED_GAME]:
        print("=" * 80)
        print(f"{eq_type.value.upper().replace('_', ' ')} EQUILIBRIUM")
        print("=" * 80)
        print()
        
        analysis = game.analyze_equilibrium(P, eq_type)
        
        # Show strategies
        print("STRATEGY DISTRIBUTIONS:")
        print("-" * 80)
        for idx, country in enumerate(game.parties):
            dominant = analysis['dominant_actions'][idx]
            probs = analysis['strategies'][idx]
            print(f"\n{country}:")
            print(f"  Dominant: {game.action_labels[dominant]} ({probs[dominant]:.1%})")
            print(f"  Full distribution:")
            for action_idx, label in game.action_labels.items():
                if action_idx in game.strategy_sets[country]:
                    print(f"    {label:30s}: {probs[action_idx]:6.1%}")
                else:
                    print(f"    {label:30s}: N/A (not available)")
        
        print("\n" + "=" * 80)
        print("EXPLANATIONS:")
        print("=" * 80)
        for country, explanation in analysis['explanations'].items():
            print(f"\n{country}:")
            print(f"  {explanation}")
        
        print("\n" + "=" * 80)
        print("COUNTRY COMPARISON:")
        print("=" * 80)
        comparison = game.compare_countries(analysis)
        print(comparison)
        print()
    
    # Show country capabilities
    print("=" * 80)
    print("COUNTRY CAPABILITIES & CONSTRAINTS:")
    print("=" * 80)
    for country, caps in game.capabilities.items():
        print(f"\n{country}:")
        print(f"  Economic Power:      {caps.economic_power:.2f}")
        print(f"  Military Power:      {caps.military_power:.2f}")
        print(f"  Diplomatic Influence: {caps.diplomatic_influence:.2f}")
        print(f"  Domestic Stability:  {caps.domestic_stability:.2f}")
        print(f"  Export Dependency:   {caps.export_dependency:.2f}")
        print(f"  Energy Dependency:   {caps.energy_dependency:.2f}")
        print(f"  Tech Leadership:     {caps.tech_leadership:.2f}")
        print(f"  Alliance Strength:   {caps.alliance_strength:.2f}")
        print(f"  Constraint Tolerance: {caps.constraint_tolerance:.2f}")
        print(f"  Available Actions:   {[game.action_labels[i] for i in game.strategy_sets[country]]}")
    
    print("\n" + "=" * 80)
    print("ALLIANCE RELATIONSHIPS:")
    print("=" * 80)
    for alliance in game.alliances:
        relationship = "Ally" if alliance.strength > 0 else "Adversary"
        print(f"{alliance.country1:8s} <-> {alliance.country2:8s}: "
              f"{relationship:10s} (strength: {alliance.strength:+.2f}, type: {alliance.type})")


if __name__ == "__main__":
    main()



