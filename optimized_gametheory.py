"""
Optimized Geopolitical Market Game Tracker
Enhanced with country-specific constraints, capabilities, alliances, and multiple equilibrium types
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import warnings
warnings.filterwarnings("ignore")

from gametheory import GeopoliticalMarketGame
from data_cache import get_cache


class EquilibriumType(Enum):
    NASH = "nash"
    BAYESIAN = "bayesian"
    REPEATED_GAME = "repeated_game"


@dataclass
class CountryCapabilities:
    """Country-specific capabilities and constraints"""
    name: str
    economic_power: float  # 0-1 scale
    military_power: float  # 0-1 scale
    diplomatic_influence: float  # 0-1 scale
    domestic_stability: float  # 0-1 scale (higher = more stable)
    export_dependency: float  # 0-1 scale (higher = more dependent on exports)
    energy_dependency: float  # 0-1 scale (higher = more dependent on energy imports)
    tech_leadership: float  # 0-1 scale
    alliance_strength: float  # 0-1 scale (strength of primary alliances)
    constraint_tolerance: float  # 0-1 scale (how much domestic constraints limit actions)


@dataclass
class AllianceEffect:
    """Alliance relationships between countries"""
    country1: str
    country2: str
    strength: float  # -1 (enemy) to +1 (strong ally)
    type: str  # "military", "economic", "diplomatic"


class OptimizedGeopoliticalGame(GeopoliticalMarketGame):
    """
    Enhanced geopolitical game with country-specific constraints and capabilities
    """
    
    def __init__(self):
        super().__init__()
        
        # Define country capabilities based on real-world constraints
        self.capabilities = {
            "USA": CountryCapabilities(
                name="USA",
                economic_power=1.0,
                military_power=1.0,
                diplomatic_influence=0.95,
                domestic_stability=0.75,  # Political polarization
                export_dependency=0.15,  # Low export dependency
                energy_dependency=0.1,  # Energy independent
                tech_leadership=0.95,
                alliance_strength=0.9,  # Strong NATO, Japan, Taiwan alliances
                constraint_tolerance=0.6  # Moderate domestic constraints
            ),
            "China": CountryCapabilities(
                name="China",
                economic_power=0.85,
                military_power=0.75,
                diplomatic_influence=0.7,
                domestic_stability=0.85,  # Authoritarian stability
                export_dependency=0.7,  # High export dependency
                energy_dependency=0.8,  # High energy import dependency
                tech_leadership=0.6,
                alliance_strength=0.3,  # Limited alliances (Russia, some African nations)
                constraint_tolerance=0.8  # Lower domestic constraints (authoritarian)
            ),
            "Japan": CountryCapabilities(
                name="Japan",
                economic_power=0.6,
                military_power=0.4,  # Constitutionally limited
                diplomatic_influence=0.5,
                domestic_stability=0.9,  # High stability
                export_dependency=0.65,  # High export dependency
                energy_dependency=0.95,  # Very high energy import dependency
                tech_leadership=0.75,
                alliance_strength=0.85,  # Strong US alliance
                constraint_tolerance=0.5  # High domestic constraints (pacifist constitution)
            ),
            "Germany": CountryCapabilities(
                name="Germany",
                economic_power=0.55,
                military_power=0.35,  # Limited by historical constraints
                diplomatic_influence=0.65,  # EU leadership
                domestic_stability=0.8,
                export_dependency=0.7,  # High export dependency
                energy_dependency=0.85,  # High energy dependency (especially after Russia)
                tech_leadership=0.7,
                alliance_strength=0.8,  # Strong EU and NATO
                constraint_tolerance=0.55  # Moderate constraints
            ),
            "Taiwan": CountryCapabilities(
                name="Taiwan",
                economic_power=0.25,
                military_power=0.2,  # Limited military
                diplomatic_influence=0.2,  # Limited recognition
                domestic_stability=0.75,
                export_dependency=0.8,  # Very high export dependency (semiconductors)
                energy_dependency=0.9,  # Very high energy dependency
                tech_leadership=0.85,  # TSMC leadership
                alliance_strength=0.7,  # Strong US support (unofficial)
                constraint_tolerance=0.4  # High constraints (small, vulnerable)
            )
        }
        
        # Define alliance relationships
        self.alliances = [
            AllianceEffect("USA", "Japan", 0.9, "military"),
            AllianceEffect("USA", "Taiwan", 0.85, "military"),
            AllianceEffect("USA", "Germany", 0.75, "military"),
            AllianceEffect("Germany", "USA", 0.75, "military"),
            AllianceEffect("Japan", "USA", 0.9, "military"),
            AllianceEffect("Taiwan", "USA", 0.85, "military"),
            AllianceEffect("China", "USA", -0.6, "economic"),  # Adversarial
            AllianceEffect("China", "Japan", -0.5, "diplomatic"),
            AllianceEffect("China", "Taiwan", -0.8, "military"),  # Strong adversarial
        ]
        
        # Country-specific strategy sets (subset of actions based on capabilities)
        self.strategy_sets = {
            "USA": [0, 1, 2, 3],  # All actions available
            "China": [0, 1, 2, 3],  # All actions available
            "Japan": [0, 1, 2],  # Limited military posturing (constitutional constraints)
            "Germany": [0, 1, 2],  # Limited military posturing (historical constraints)
            "Taiwan": [1, 2],  # Limited to de-escalate and stimulus (vulnerability)
        }
        
        # Action labels for clarity
        self.action_labels = {
            0: "Hawkish Rhetoric / Sanctions",
            1: "De-escalate / Dialogue",
            2: "Economic Stimulus",
            3: "Military Posturing"
        }
    
    def get_alliance_multiplier(self, country1: str, country2: str, action_type: int) -> float:
        """Get alliance effect multiplier for country1's action affecting country2"""
        # Find alliance relationship
        for alliance in self.alliances:
            if (alliance.country1 == country1 and alliance.country2 == country2) or \
               (alliance.country1 == country2 and alliance.country2 == country1):
                strength = alliance.strength
                
                # Action-specific effects
                if action_type == 0:  # Hawkish
                    # Allies benefit from each other's hawkish stance against common enemies
                    if strength > 0:
                        return 1.0 + 0.3 * strength
                    else:  # Adversarial
                        return 1.0 - 0.5 * abs(strength)
                elif action_type == 1:  # De-escalate
                    # Allies coordinate on de-escalation
                    if strength > 0:
                        return 1.0 + 0.2 * strength
                    else:
                        return 1.0 + 0.1 * abs(strength)  # Even adversaries benefit from de-escalation
                elif action_type == 2:  # Stimulus
                    # Economic coordination benefits allies
                    if strength > 0:
                        return 1.0 + 0.15 * strength
                elif action_type == 3:  # Military
                    # Military coordination for allies, escalation for adversaries
                    if strength > 0:
                        return 1.0 + 0.4 * strength
                    else:
                        return 1.0 - 0.6 * abs(strength)
        
        return 1.0  # Neutral relationship
    
    def build_country_payoff_matrix(self, country_idx: int, market: Dict[str, float]) -> np.ndarray:
        """
        Build country-specific payoff matrix row based on capabilities and constraints
        Returns: 1x4 array of payoffs for each action
        """
        country = self.parties[country_idx]
        caps = self.capabilities[country]
        
        # Get market signals
        country_return = market.get(country, 0.0)
        vix = market.get("VIX", 0.0)
        gold = market.get("Gold", 0.0)
        
        # Currency effects
        if country == "China":
            currency_effect = -market.get("USDCNY", 0.0) * 5
        elif country == "Japan":
            currency_effect = market.get("USDJPY", 0.0) * 5
        else:
            currency_effect = 0.0
        
        # Calculate relative performance
        all_returns = [market.get(c, 0.0) for c in self.parties]
        avg_return = np.mean(all_returns)
        relative_perf = country_return - avg_return
        
        # Normalize VIX (typical range 10-30)
        vix_normalized = (vix - 20.0) / 10.0
        vix_normalized = np.clip(vix_normalized, -2.0, 2.0)
        
        payoffs = np.zeros(4)
        
        # Action 0: Hawkish Rhetoric / Sanctions
        if 0 in self.strategy_sets[country]:
            hawk_base = (
                2.0 * vix_normalized * caps.military_power +  # Military power amplifies hawkish effectiveness
                1.5 * gold * caps.economic_power +
                -0.8 * abs(country_return) * caps.export_dependency +  # Export-dependent countries hurt by volatility
                0.5 * currency_effect * caps.export_dependency +
                0.3 * (avg_return - country_return) * caps.economic_power  # Benefit if others struggling
            )
            # Domestic constraints reduce hawkish appeal
            hawk_base *= (1.0 - 0.3 * (1.0 - caps.constraint_tolerance))
            # Alliance effects
            alliance_boost = 0.0
            for other_country in self.parties:
                if other_country != country:
                    multiplier = self.get_alliance_multiplier(country, other_country, 0)
                    alliance_boost += (multiplier - 1.0) * 0.1
            hawk_base += alliance_boost
            payoffs[0] = hawk_base
        else:
            payoffs[0] = -10.0  # Action not available
        
        # Action 1: De-escalate / Dialogue
        if 1 in self.strategy_sets[country]:
            deescalate_base = (
                1.5 * country_return * caps.economic_power +
                -1.2 * vix_normalized * caps.export_dependency +  # Export-dependent countries benefit from stability
                0.4 * relative_perf * caps.diplomatic_influence +
                0.3 * caps.domestic_stability  # Stable countries prefer de-escalation
            )
            # More attractive when volatility is high
            if vix_normalized > 0.5:
                deescalate_base += 1.0 * caps.export_dependency
            # Alliance coordination
            alliance_boost = 0.0
            for other_country in self.parties:
                if other_country != country:
                    multiplier = self.get_alliance_multiplier(country, other_country, 1)
                    alliance_boost += (multiplier - 1.0) * 0.15
            deescalate_base += alliance_boost
            payoffs[1] = deescalate_base
        else:
            payoffs[1] = -10.0
        
        # Action 2: Economic Stimulus
        if 2 in self.strategy_sets[country]:
            stimulus_base = (
                2.5 * max(0, -country_return) * caps.economic_power +  # More effective when market is down
                1.2 * country_return * caps.economic_power +
                0.5 * caps.economic_power +
                -0.3 * caps.energy_dependency * abs(gold)  # Energy-dependent countries hurt by commodity volatility
            )
            # More effective when relative performance is poor
            if relative_perf < -0.01:
                stimulus_base += 1.0 * caps.economic_power
            # Alliance economic coordination
            alliance_boost = 0.0
            for other_country in self.parties:
                if other_country != country:
                    multiplier = self.get_alliance_multiplier(country, other_country, 2)
                    alliance_boost += (multiplier - 1.0) * 0.1
            stimulus_base += alliance_boost
            payoffs[2] = stimulus_base
        else:
            payoffs[2] = -10.0
        
        # Action 3: Military Posturing
        if 3 in self.strategy_sets[country]:
            military_base = (
                3.0 * vix_normalized * caps.military_power +
                2.0 * gold * caps.military_power +
                -1.5 * abs(country_return) * caps.export_dependency +
                -0.5 * country_return * caps.energy_dependency  # Energy-dependent countries avoid military escalation
            )
            # Only attractive in extreme scenarios for countries with military capability
            if vix_normalized > 1.0 and gold > 0.02:
                military_base += 2.0 * caps.military_power
            else:
                military_base -= 1.0 * caps.constraint_tolerance  # Domestic constraints reduce appeal
            
            # Strong alliance effects for military actions
            alliance_boost = 0.0
            for other_country in self.parties:
                if other_country != country:
                    multiplier = self.get_alliance_multiplier(country, other_country, 3)
                    alliance_boost += (multiplier - 1.0) * 0.2
            military_base += alliance_boost
            payoffs[3] = military_base
        else:
            payoffs[3] = -10.0
        
        return payoffs
    
    def build_current_payoff_matrix(self):
        """Build enhanced payoff matrix with country-specific constraints"""
        market = self.fetch_real_time_data(days=14)
        
        # Build 5x4 matrix with country-specific payoffs
        P = np.zeros((5, 4))
        
        for i, country in enumerate(self.parties):
            P[i, :] = self.build_country_payoff_matrix(i, market)
        
        # Add small random noise for robustness
        P += np.random.normal(0, 0.05, P.shape)
        
        return P
    
    def solve_nash_equilibrium(self, P: np.ndarray) -> np.ndarray:
        """Solve Nash equilibrium using improved fictitious play"""
        n_players, n_actions = P.shape
        
        # Initialize strategies with softmax based on base payoffs
        strategies = np.zeros((n_players, n_actions))
        for player in range(n_players):
            base_payoffs = P[player, :]
            # Softmax initialization
            exp_payoffs = np.exp(2.0 * (base_payoffs - np.max(base_payoffs)))
            strategies[player] = exp_payoffs / exp_payoffs.sum()
        
        cumulative_strategy = strategies.copy()
        learning_rate = 0.1
        
        for iteration in range(5000):
            expected_payoffs = np.zeros((n_players, n_actions))
            
            for player in range(n_players):
                for action in range(n_actions):
                    base_payoff = P[player, action]
                    
                    # Interaction effect: if others play same action, reduce payoff (competition)
                    interaction_effect = 0.0
                    for other_player in range(n_players):
                        if other_player != player:
                            for other_action in range(n_actions):
                                prob = strategies[other_player, other_action]
                                if other_action == action:
                                    interaction_effect -= 0.1 * prob
                                elif (action == 0 and other_action == 1) or (action == 1 and other_action == 0):
                                    interaction_effect += 0.15 * prob
                    
                    expected_payoffs[player, action] = base_payoff + interaction_effect
            
            # Update strategies using fictitious play
            for player in range(n_players):
                best_action = np.argmax(expected_payoffs[player])
                new_strategy = np.zeros(n_actions)
                new_strategy[best_action] = 1.0
                
                strategies[player] = (1 - learning_rate) * strategies[player] + learning_rate * new_strategy
                strategies[player] = 0.95 * strategies[player] + 0.05 * np.ones(n_actions) / n_actions
                strategies[player] = strategies[player] / strategies[player].sum()
                
                cumulative_strategy[player] += strategies[player]
            
            if iteration % 500 == 0:
                learning_rate *= 0.95
        
        # Return average strategy
        avg_strategy = cumulative_strategy / cumulative_strategy.sum(axis=1, keepdims=True)
        avg_strategy = np.maximum(avg_strategy, 0.01)
        avg_strategy = avg_strategy / avg_strategy.sum(axis=1, keepdims=True)
        
        return avg_strategy
    
    def solve_bayesian_equilibrium(self, P: np.ndarray, uncertainty: float = 0.2) -> np.ndarray:
        """
        Solve Bayesian Nash equilibrium with uncertainty about other players' types
        """
        n_players, n_actions = P.shape
        
        # Add uncertainty to payoffs (representing incomplete information)
        P_uncertain = P + np.random.normal(0, uncertainty, P.shape)
        
        # Solve as Nash with uncertain payoffs
        return self.solve_nash_equilibrium(P_uncertain)
    
    def solve_repeated_game_equilibrium(self, P: np.ndarray, discount_factor: float = 0.95) -> np.ndarray:
        """
        Solve for equilibrium in repeated game setting (considering future interactions)
        """
        n_players, n_actions = P.shape
        
        # In repeated games, cooperation becomes more attractive
        # Adjust payoffs to account for future relationship value
        P_repeated = P.copy()
        
        for i in range(n_players):
            for j in range(n_players):
                if i != j:
                    alliance_mult = self.get_alliance_multiplier(self.parties[i], self.parties[j], 1)
                    # De-escalation becomes more valuable in repeated interactions
                    P_repeated[i, 1] += 0.3 * (alliance_mult - 1.0) * discount_factor
        
        return self.solve_nash_equilibrium(P_repeated)
    
    def analyze_equilibrium(self, P: np.ndarray, eq_type: EquilibriumType = EquilibriumType.NASH) -> Dict:
        """
        Solve equilibrium and provide detailed analysis
        """
        if eq_type == EquilibriumType.NASH:
            strategies = self.solve_nash_equilibrium(P)
        elif eq_type == EquilibriumType.BAYESIAN:
            strategies = self.solve_bayesian_equilibrium(P)
        elif eq_type == EquilibriumType.REPEATED_GAME:
            strategies = self.solve_repeated_game_equilibrium(P)
        else:
            strategies = self.solve_nash_equilibrium(P)
        
        # Analyze results
        analysis = {
            'strategies': strategies,
            'dominant_actions': [np.argmax(strategies[i]) for i in range(len(self.parties))],
            'action_probabilities': {
                country: {
                    self.action_labels[i]: float(strategies[idx, i])
                    for i in range(4)
                    if i in self.strategy_sets[country]
                }
                for idx, country in enumerate(self.parties)
            },
            'explanations': self._generate_explanations(strategies, P),
            'equilibrium_type': eq_type.value
        }
        
        return analysis
    
    def _generate_explanations(self, strategies: np.ndarray, P: np.ndarray) -> Dict[str, str]:
        """Generate explanations for why each country's strategy differs"""
        explanations = {}
        
        for idx, country in enumerate(self.parties):
            caps = self.capabilities[country]
            dominant_action = np.argmax(strategies[idx])
            prob_dist = strategies[idx]
            
            explanation_parts = []
            
            # Why this action is dominant
            explanation_parts.append(
                f"{country} favors {self.action_labels[dominant_action]} "
                f"({prob_dist[dominant_action]:.1%} probability)"
            )
            
            # Capability-based explanation
            if dominant_action == 0:  # Hawkish
                explanation_parts.append(
                    f"High military power ({caps.military_power:.2f}) and "
                    f"alliance strength ({caps.alliance_strength:.2f}) enable aggressive stance."
                )
            elif dominant_action == 1:  # De-escalate
                explanation_parts.append(
                    f"High export dependency ({caps.export_dependency:.2f}) and "
                    f"domestic stability ({caps.domestic_stability:.2f}) favor stability."
                )
            elif dominant_action == 2:  # Stimulus
                explanation_parts.append(
                    f"Economic power ({caps.economic_power:.2f}) enables stimulus, "
                    f"especially given export dependency ({caps.export_dependency:.2f})."
                )
            elif dominant_action == 3:  # Military
                explanation_parts.append(
                    f"Military power ({caps.military_power:.2f}) and "
                    f"low constraint tolerance ({1-caps.constraint_tolerance:.2f}) enable military posturing."
                )
            
            # Constraint explanation
            if caps.constraint_tolerance < 0.5:
                explanation_parts.append(
                    f"High domestic constraints limit available actions "
                    f"(available: {[self.action_labels[i] for i in self.strategy_sets[country]]})."
                )
            
            # Alliance explanation
            relevant_alliances = [a for a in self.alliances if a.country1 == country or a.country2 == country]
            if relevant_alliances:
                strong_allies = [a.country2 if a.country1 == country else a.country1 
                               for a in relevant_alliances if a.strength > 0.7]
                if strong_allies:
                    explanation_parts.append(
                        f"Strong alliances with {', '.join(strong_allies)} "
                        f"influence strategy choices."
                    )
            
            explanations[country] = " ".join(explanation_parts)
        
        return explanations
    
    def compare_countries(self, analysis: Dict) -> str:
        """Generate comparison of why countries differ"""
        comparisons = []
        
        dominant_actions = analysis['dominant_actions']
        action_counts = {}
        for action in dominant_actions:
            action_counts[action] = action_counts.get(action, 0) + 1
        
        comparisons.append("Country Strategy Comparison:")
        comparisons.append("=" * 60)
        
        for idx, country in enumerate(self.parties):
            action = dominant_actions[idx]
            prob = analysis['strategies'][idx, action]
            comparisons.append(
                f"{country:10s}: {self.action_labels[action]:30s} "
                f"({prob:.1%})"
            )
        
        comparisons.append("\nKey Differences:")
        comparisons.append("-" * 60)
        
        # Compare USA vs China
        usa_idx = self.parties.index("USA")
        china_idx = self.parties.index("China")
        if dominant_actions[usa_idx] != dominant_actions[china_idx]:
            comparisons.append(
                f"USA vs China: USA favors {self.action_labels[dominant_actions[usa_idx]]} "
                f"while China favors {self.action_labels[dominant_actions[china_idx]]}. "
                f"This reflects USA's stronger alliances and military power, "
                f"while China's export dependency makes it more cautious."
            )
        
        # Compare small vs large powers
        taiwan_idx = self.parties.index("Taiwan")
        if dominant_actions[taiwan_idx] == 1:  # De-escalate
            comparisons.append(
                f"Taiwan's vulnerability (small size, high export/energy dependency) "
                f"forces a de-escalation strategy despite strong US support."
            )
        
        # Compare constrained vs unconstrained
        japan_idx = self.parties.index("Japan")
        if 3 not in self.strategy_sets["Japan"]:
            comparisons.append(
                f"Japan's constitutional constraints prevent military posturing, "
                f"limiting its strategy set compared to USA and China."
            )
        
        return "\n".join(comparisons)

