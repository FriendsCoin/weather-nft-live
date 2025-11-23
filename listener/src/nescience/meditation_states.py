"""
5 Meditation States for NESCIENCE

Not alpha+/beta- optimization.
Phenomenological descriptions of conscious states.

SETTLING - Beginning to calm, but turbulent
FLOW - Natural movement of attention
DEEP - Profound stillness, low activity
LIMINAL - Between sleep and waking
PRESENT - Pure presence, no object

Based on Vipassana practice and EEG correlates.
Not diagnostic. Not prescriptive. Just witnessing.
"""

import numpy as np
from typing import Dict, Tuple, Optional
from enum import Enum
from dataclasses import dataclass


class MeditationState(Enum):
    """5 phenomenological meditation states"""
    SETTLING = "SETTLING"  # Turbulent beginning
    FLOW = "FLOW"          # Natural movement
    DEEP = "DEEP"          # Profound stillness
    LIMINAL = "LIMINAL"    # Threshold state
    PRESENT = "PRESENT"    # Pure presence


@dataclass
class StateSignature:
    """EEG signature for each meditation state"""
    state: MeditationState
    intensity: float  # How clearly this state is present (0-1)
    qualities: Dict[str, float]  # Phenomenological qualities


class MeditationStateClassifier:
    """
    Classifies EEG into 5 meditation states

    NOT wellness optimization. NOT diagnostic.
    Poetic interpretation of consciousness flux.

    States are based on:
    - Vipassana meditation phenomenology
    - EEG research (alpha, theta, gamma coherence)
    - Anicca - all states are impermanent
    """

    def __init__(self):
        """Initialize classifier"""
        self.state_history = []
        self.current_state = MeditationState.SETTLING

        print("🧘 NESCIENCE meditation state classifier initialized")
        print("   States: SETTLING → FLOW → DEEP/LIMINAL → PRESENT")
        print("   Witnessing without judgment...")

    def classify(
        self,
        alpha: float,
        beta: float,
        theta: float,
        delta: float,
        gamma: Optional[float] = None
    ) -> StateSignature:
        """
        Classify current meditation state

        Args:
            alpha: Alpha power (8-12 Hz) - relaxation
            beta: Beta power (13-30 Hz) - active mind
            theta: Theta power (4-8 Hz) - deep meditation
            delta: Delta power (0.5-4 Hz) - sleep/drowsiness
            gamma: Gamma power (30-50 Hz) - insight moments

        Returns:
            StateSignature with state and intensity
        """

        # Compute state probabilities
        state_scores = self._compute_state_scores(alpha, beta, theta, delta, gamma)

        # Get dominant state
        dominant_state = max(state_scores.items(), key=lambda x: x[1])
        state = dominant_state[0]
        intensity = dominant_state[1]

        # Compute phenomenological qualities
        qualities = self._compute_qualities(alpha, beta, theta, delta, gamma)

        signature = StateSignature(
            state=state,
            intensity=intensity,
            qualities=qualities
        )

        # Update history
        self.state_history.append(signature)
        self.current_state = state

        return signature

    def _compute_state_scores(
        self,
        alpha: float,
        beta: float,
        theta: float,
        delta: float,
        gamma: Optional[float]
    ) -> Dict[MeditationState, float]:
        """
        Compute probability for each meditation state

        This is phenomenological, not diagnostic:
        - SETTLING: High beta, variable alpha (mind settling)
        - FLOW: Balanced alpha-theta (natural movement)
        - DEEP: High theta, low beta (profound stillness)
        - LIMINAL: High delta, moderate theta (threshold)
        - PRESENT: Balanced all, occasional gamma (pure presence)
        """

        scores = {}

        # SETTLING - Mind beginning to calm
        # High beta (mental activity) with emerging alpha
        settling_score = (
            0.4 * beta +           # Mental activity
            0.3 * alpha +          # Beginning relaxation
            0.2 * (1 - theta) +    # Not yet deep
            0.1 * (1 - delta)      # Awake
        )
        scores[MeditationState.SETTLING] = settling_score

        # FLOW - Natural attention movement
        # Balanced alpha-theta, low beta
        theta_alpha_balance = 1 - abs(theta - alpha)
        flow_score = (
            0.4 * theta_alpha_balance +  # Balanced states
            0.3 * alpha +                # Relaxed
            0.2 * (1 - beta) +           # Calm mind
            0.1 * theta                  # Some depth
        )
        scores[MeditationState.FLOW] = flow_score

        # DEEP - Profound stillness
        # High theta, low beta, moderate alpha
        deep_score = (
            0.5 * theta +          # Deep meditation
            0.3 * alpha +          # Relaxed awareness
            0.2 * (1 - beta)       # Very calm
        )
        scores[MeditationState.DEEP] = deep_score

        # LIMINAL - Between sleep and waking
        # High delta with some theta (threshold state)
        liminal_score = (
            0.5 * delta +          # Drowsy
            0.3 * theta +          # Deep
            0.2 * (1 - beta)       # Not thinking
        )
        scores[MeditationState.LIMINAL] = liminal_score

        # PRESENT - Pure presence
        # Balanced all bands, no dominance (equanimity)
        # Optional gamma spikes (insight moments)
        balance = 1 - np.std([alpha, beta, theta, delta])
        gamma_boost = gamma if gamma else 0.0
        present_score = (
            0.5 * balance +        # Balanced awareness
            0.3 * alpha +          # Relaxed presence
            0.1 * theta +          # Some depth
            0.1 * gamma_boost      # Occasional insights
        )
        scores[MeditationState.PRESENT] = present_score

        # Normalize to 0-1
        total = sum(scores.values())
        if total > 0:
            scores = {k: v/total for k, v in scores.items()}

        return scores

    def _compute_qualities(
        self,
        alpha: float,
        beta: float,
        theta: float,
        delta: float,
        gamma: Optional[float]
    ) -> Dict[str, float]:
        """
        Compute phenomenological qualities

        Not diagnostic metrics. Poetic dimensions:
        - turbulence: How chaotic/settled (high beta = turbulent)
        - depth: How deep the meditation (high theta = deep)
        - clarity: How clear the awareness (balanced = clear)
        - dreaminess: How close to sleep (high delta = dreamy)
        - luminosity: Moments of insight (gamma spikes = luminous)
        """

        qualities = {
            'turbulence': beta,  # Mental activity
            'depth': theta,  # Meditation depth
            'clarity': 1 - abs(0.5 - alpha),  # Optimal alpha
            'dreaminess': delta,  # Drowsiness
            'luminosity': gamma if gamma else 0.0,  # Insight moments
            'stillness': 1 - beta,  # Mental calm
            'fluidity': alpha * theta,  # Flow state
        }

        return qualities

    def get_state_description(self, state: MeditationState) -> str:
        """
        Get phenomenological description of state

        Not "good" or "bad". Just description.
        Anicca - all states arise and pass.
        """

        descriptions = {
            MeditationState.SETTLING: (
                "The mind begins to gather itself. "
                "Thoughts still arise like ripples on a pond. "
                "Not yet still, but settling."
            ),

            MeditationState.FLOW: (
                "Attention moves naturally, like water finding its course. "
                "No forcing, no fixing. "
                "Just the flow of awareness."
            ),

            MeditationState.DEEP: (
                "Profound stillness. "
                "The depths where few thoughts venture. "
                "Silent, but not empty."
            ),

            MeditationState.LIMINAL: (
                "Between sleep and waking. "
                "The threshold where consciousness dissolves. "
                "Dreamlike, but aware."
            ),

            MeditationState.PRESENT: (
                "Nothing special. Just this. "
                "Pure presence without object. "
                "Awareness aware of awareness."
            )
        }

        return descriptions.get(state, "Unknown state")

    def get_transition_poetry(self, from_state: MeditationState, to_state: MeditationState) -> str:
        """
        Poetic description of state transitions

        Anicca - impermanence in action
        """

        transitions = {
            (MeditationState.SETTLING, MeditationState.FLOW): "The turbulence begins to find rhythm...",
            (MeditationState.FLOW, MeditationState.DEEP): "The stream descends into silence...",
            (MeditationState.DEEP, MeditationState.PRESENT): "Depth dissolves into simple presence...",
            (MeditationState.FLOW, MeditationState.LIMINAL): "The boundary grows thin...",
            (MeditationState.LIMINAL, MeditationState.DEEP): "Awakening from the threshold...",
            (MeditationState.PRESENT, MeditationState.SETTLING): "And the cycle begins again...",
        }

        transition_key = (from_state, to_state)
        return transitions.get(transition_key, "The state shifts, as all states do...")

    def get_recent_pattern(self, window: int = 10) -> Dict[MeditationState, float]:
        """
        Get distribution of states over recent window

        Useful for understanding session trajectory
        """
        if len(self.state_history) < window:
            window = len(self.state_history)

        if window == 0:
            return {}

        recent = self.state_history[-window:]

        state_counts = {}
        for signature in recent:
            state = signature.state
            state_counts[state] = state_counts.get(state, 0) + 1

        # Convert to proportions
        state_proportions = {k: v/window for k, v in state_counts.items()}

        return state_proportions
