# Optimized Geopolitical Market Game Tracker

## Overview

The optimized model enhances the original game theory framework with country-specific constraints, capabilities, alliances, and multiple equilibrium solution methods.

## Key Enhancements

### 1. Country-Specific Payoff Matrices

Each country now has a unique payoff matrix based on:
- **Economic Power**: Ability to use economic tools effectively
- **Military Power**: Capability for military actions
- **Diplomatic Influence**: Soft power and diplomatic leverage
- **Domestic Stability**: Internal political constraints
- **Export Dependency**: Vulnerability to trade disruptions
- **Energy Dependency**: Vulnerability to energy supply shocks
- **Tech Leadership**: Technological advantages
- **Alliance Strength**: Support from allies
- **Constraint Tolerance**: How much domestic constraints limit actions

### 2. Tailored Strategy Sets

Countries have different available actions based on their capabilities:

- **USA**: All 4 actions available (Hawkish, De-escalate, Stimulus, Military)
- **China**: All 4 actions available
- **Japan**: Limited to 3 actions (excludes Military due to constitutional constraints)
- **Germany**: Limited to 3 actions (excludes Military due to historical constraints)
- **Taiwan**: Limited to 2 actions (only De-escalate and Stimulus due to vulnerability)

### 3. Domestic Constraint Parameters

Each country has constraint tolerance that affects:
- Which actions are available
- How attractive certain actions are
- Risk tolerance for aggressive strategies

**Examples:**
- Japan: High constraints (pacifist constitution) → No military posturing
- Taiwan: Very high constraints (small, vulnerable) → Only defensive actions
- USA: Moderate constraints → Full range of actions
- China: Lower constraints (authoritarian) → More flexibility

### 4. Alliance Effects

Alliance relationships modify payoffs:

**Strong Alliances:**
- USA-Japan (0.9): Military coordination, economic cooperation
- USA-Taiwan (0.85): Security guarantee, tech cooperation
- USA-Germany (0.75): NATO, economic coordination

**Adversarial Relationships:**
- China-USA (-0.6): Trade tensions, strategic competition
- China-Taiwan (-0.8): Territorial dispute, military threat

**Alliance Effects by Action:**
- **Hawkish**: Allies benefit from coordinated hawkish stance (+30% boost)
- **De-escalate**: Allies coordinate on stability (+20% boost)
- **Stimulus**: Economic coordination benefits allies (+15% boost)
- **Military**: Strong coordination for allies (+40% boost), escalation for adversaries (-60%)

### 5. Multiple Equilibrium Types

#### Nash Equilibrium
- Standard non-cooperative equilibrium
- Each country maximizes own payoff given others' strategies
- Best for one-shot interactions

#### Bayesian Nash Equilibrium
- Accounts for uncertainty about other players' types
- Adds noise to payoff matrices (20% uncertainty)
- Better for situations with incomplete information

#### Repeated Game Equilibrium
- Considers future relationship value
- Cooperation becomes more attractive (discount factor 0.95)
- De-escalation gains value in long-term relationships
- Better for ongoing geopolitical relationships

### 6. Country Comparison & Explanations

The model generates explanations for:
- Why each country favors its dominant strategy
- How capabilities influence strategy choice
- How constraints limit available actions
- How alliances affect strategy selection
- Why predictions differ between countries

## Country Profiles

### USA
- **Strengths**: Highest economic/military power, strong alliances, tech leadership
- **Constraints**: Moderate domestic polarization
- **Strategy**: Can pursue all actions; favors hawkish when allies support, stimulus when economy weak

### China
- **Strengths**: High economic power, authoritarian stability, tech capabilities
- **Constraints**: High export/energy dependency, limited alliances
- **Strategy**: Balances hawkish (territorial) with de-escalate (economic stability)

### Japan
- **Strengths**: Tech leadership, strong US alliance, high stability
- **Constraints**: Constitutional limits on military, high energy dependency
- **Strategy**: Favors de-escalate and stimulus; cannot use military posturing

### Germany
- **Strengths**: EU leadership, strong alliances, tech capabilities
- **Constraints**: Historical limits on military, high energy dependency
- **Strategy**: Favors de-escalate and economic coordination; limited military options

### Taiwan
- **Strengths**: Tech leadership (TSMC), strong US support
- **Constraints**: Small size, extreme vulnerability, high export/energy dependency
- **Strategy**: Primarily de-escalate and stimulus; avoids provocative actions

## Usage

### Python API
```python
from optimized_gametheory import OptimizedGeopoliticalGame, EquilibriumType

game = OptimizedGeopoliticalGame()
P = game.build_current_payoff_matrix()
analysis = game.analyze_equilibrium(P, EquilibriumType.NASH)
print(analysis['explanations'])
print(game.compare_countries(analysis))
```

### REST API
```bash
POST /api/optimized-analysis
{
  "equilibrium_type": "nash",  # or "bayesian" or "repeated_game"
  "date": "2024-11-21"  # optional
}
```

### Demo Script
```bash
python3 optimized_analysis.py
```

## Key Differences from Original Model

1. **Country-Specific Payoffs**: Each country's payoffs reflect its unique constraints and capabilities
2. **Limited Strategy Sets**: Countries can't use actions they're incapable of
3. **Alliance Effects**: Actions are more/less effective based on alliance relationships
4. **Multiple Equilibria**: Different solution concepts for different scenarios
5. **Rich Explanations**: Detailed analysis of why countries differ

## Example Output

```
USA: USA favors Hawkish Rhetoric / Sanctions (65.2% probability)
     High military power (1.00) and alliance strength (0.90) enable aggressive stance.
     Strong alliances with Japan, Taiwan influence strategy choices.

China: China favors De-escalate / Dialogue (58.7% probability)
       High export dependency (0.70) and domestic stability (0.85) favor stability.
       Limited alliances reduce hawkish appeal.

Taiwan: Taiwan favors De-escalate / Dialogue (72.3% probability)
        High export dependency (0.80) and domestic stability (0.75) favor stability.
        High domestic constraints limit available actions.
        Strong alliances with USA influence strategy choices.
```



