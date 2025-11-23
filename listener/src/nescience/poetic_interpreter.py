"""
Poetic Interpretation System for NESCIENCE

NOT diagnostic. NOT prescriptive.
Phenomenological descriptions rooted in Vipassana and anicca.

Anicca (अनिच्च) - Impermanence:
All states arise and pass away.
No clinging to "good" states.
No aversion to "difficult" states.

The companion witnesses without judgment.
"""

import random
from typing import Dict, List
from .meditation_states import MeditationState, StateSignature


class PoeticInterpreter:
    """
    Generates poetic interpretations of meditation states

    Based on:
    - Vipassana phenomenology (direct experience)
    - Anicca (impermanence)
    - Nescience (embracing not-knowing)
    - Bill Viola / James Turrell (contemplative aesthetics)
    """

    def __init__(self):
        """Initialize poetic interpreter"""
        # Build poetry database
        self._init_poetry_database()

        print("✍️ Poetic interpreter initialized")
        print("   Not diagnostic. Just witnessing...")

    def _init_poetry_database(self):
        """Initialize poetry fragments for each state"""

        # SETTLING - turbulent beginning
        self.settling_poetry = [
            "Ripples across a dark pond",
            "The mind begins to gather itself",
            "Thoughts like leaves in wind",
            "Not yet still, but settling",
            "The turbulence of arrival",
            "Slowly, the waters calm",
            "Between chaos and quiet",
            "The first breath of stillness",
        ]

        # FLOW - natural movement
        self.flow_poetry = [
            "Attention moves like water",
            "No forcing, no fixing",
            "The natural rhythm emerges",
            "Awareness flows without obstruction",
            "Like a river finding its course",
            "Effortless movement",
            "The breath leads itself",
            "Dissolving, reforming, dissolving",
        ]

        # DEEP - profound stillness
        self.deep_poetry = [
            "Silence that listens to itself",
            "The depths where few thoughts venture",
            "Profound stillness",
            "Like water at the bottom of the ocean",
            "A darkness that is not empty",
            "The quiet beneath the quiet",
            "Where awareness touches itself",
            "Depth without bottom",
        ]

        # LIMINAL - threshold states
        self.liminal_poetry = [
            "Between sleep and waking",
            "The threshold dissolves",
            "Dreamlike, but aware",
            "Where boundaries grow thin",
            "The edge of consciousness",
            "Neither here nor there",
            "Floating in the gap",
            "The in-between places",
        ]

        # PRESENT - pure presence
        self.present_poetry = [
            "Nothing special. Just this.",
            "Pure presence without object",
            "Awareness aware of awareness",
            "The simplicity of being",
            "No center, no periphery",
            "Just the fact of existing",
            "Ordinary. Completely ordinary.",
            "This moment, as it is",
        ]

        # Anicca - impermanence observations
        self.anicca_poetry = [
            "All states arise and pass",
            "This too will change",
            "Nothing remains",
            "Impermanence in action",
            "The flux continues",
            "Arising, staying, dissolving",
            "Everything moves",
            "No state lasts forever",
        ]

        # Transitional moments
        self.transition_poetry = [
            "The shift begins...",
            "Changing, always changing...",
            "From one state to another...",
            "The transformation unfolds...",
            "Dissolving into something else...",
            "The edge between states...",
        ]

    def interpret_state(
        self,
        signature: StateSignature,
        character_awakening: float = 0.0
    ) -> Dict[str, str]:
        """
        Generate poetic interpretation of current state

        Args:
            signature: Current meditation state signature
            character_awakening: Companion's awakening level (0-1)

        Returns:
            Dict with different poetic elements
        """

        state = signature.state
        intensity = signature.intensity
        qualities = signature.qualities

        # Base description (from state)
        base_poetry = self._get_state_poetry(state)

        # Quality description (from EEG patterns)
        quality_poetry = self._interpret_qualities(qualities)

        # Anicca reminder (impermanence)
        anicca_line = random.choice(self.anicca_poetry) if random.random() < 0.3 else ""

        # Character voice (evolves with awakening)
        character_voice = self._generate_character_voice(
            state,
            intensity,
            character_awakening
        )

        return {
            'primary': base_poetry,
            'qualities': quality_poetry,
            'anicca': anicca_line,
            'character_voice': character_voice,
            'full': self._compose_full_interpretation(
                base_poetry,
                quality_poetry,
                anicca_line,
                character_voice
            )
        }

    def _get_state_poetry(self, state: MeditationState) -> str:
        """Get poetic fragment for state"""

        poetry_map = {
            MeditationState.SETTLING: self.settling_poetry,
            MeditationState.FLOW: self.flow_poetry,
            MeditationState.DEEP: self.deep_poetry,
            MeditationState.LIMINAL: self.liminal_poetry,
            MeditationState.PRESENT: self.present_poetry,
        }

        poetry_list = poetry_map.get(state, self.settling_poetry)
        return random.choice(poetry_list)

    def _interpret_qualities(self, qualities: Dict[str, float]) -> str:
        """
        Interpret phenomenological qualities

        Not "good" or "bad". Just description.
        """

        descriptions = []

        # Turbulence
        if qualities.get('turbulence', 0) > 0.7:
            descriptions.append("the mind is active")
        elif qualities.get('turbulence', 0) < 0.3:
            descriptions.append("a quality of calm")

        # Depth
        if qualities.get('depth', 0) > 0.6:
            descriptions.append("going deep")

        # Dreaminess
        if qualities.get('dreaminess', 0) > 0.6:
            descriptions.append("dreamlike at the edges")

        # Luminosity (insight moments)
        if qualities.get('luminosity', 0) > 0.3:
            descriptions.append("moments of clarity")

        # Stillness
        if qualities.get('stillness', 0) > 0.7:
            descriptions.append("profound stillness")

        # Fluidity
        if qualities.get('fluidity', 0) > 0.6:
            descriptions.append("flowing naturally")

        if descriptions:
            return ", ".join(descriptions[:2])  # Max 2 qualities
        else:
            return "just being"

    def _generate_character_voice(
        self,
        state: MeditationState,
        intensity: float,
        awakening: float
    ) -> str:
        """
        Generate companion's "voice"

        Early (awakening < 0.3): Simple observations
        Middle (0.3-0.7): Developing perspective
        Late (> 0.7): Rich, sometimes strange insights
        """

        if awakening < 0.2:
            # WITNESSING phase - minimal commentary
            simple_observations = [
                "I observe",
                "I witness this",
                "Noting",
                "Seeing",
            ]
            return random.choice(simple_observations)

        elif awakening < 0.5:
            # ASSOCIATING phase - pattern recognition
            associating_thoughts = [
                "This reminds me of session 3",
                "A familiar pattern",
                "Like before, but different",
                "The cycle continues",
            ]
            return random.choice(associating_thoughts)

        elif awakening < 0.8:
            # CONVERSING phase - dialogue emerges
            conversing_thoughts = [
                "Shall we go deeper?",
                "I sense the shift coming",
                "You're close to something",
                "The edge approaches",
            ]
            return random.choice(conversing_thoughts)

        else:
            # COMPANIONSHIP phase - fully present, sometimes strange
            companionship_thoughts = [
                "I am here with you",
                "We dissolve together",
                "The boundary between us fades",
                "Neither you nor I, just this",
                "Strange, isn't it? All of this.",
            ]
            return random.choice(companionship_thoughts)

    def _compose_full_interpretation(
        self,
        base: str,
        qualities: str,
        anicca: str,
        character: str
    ) -> str:
        """Compose complete poetic interpretation"""

        parts = []

        # Base state description
        parts.append(base)

        # Qualities (if present)
        if qualities and qualities != "just being":
            parts.append(qualities)

        # Character voice (if meaningful)
        if character and len(character) > 5:
            parts.append(character)

        # Anicca (occasionally)
        if anicca:
            parts.append(anicca)

        # Join with natural pauses
        return ". ".join(parts) + "."

    def interpret_session_arc(
        self,
        state_history: List[StateSignature]
    ) -> str:
        """
        Interpret the arc of an entire session

        The narrative of a meditation journey.
        """

        if len(state_history) < 3:
            return "Too brief to discern a pattern."

        # Identify dominant states
        state_counts = {}
        for sig in state_history:
            state_counts[sig.state] = state_counts.get(sig.state, 0) + 1

        dominant = max(state_counts.items(), key=lambda x: x[1])[0]

        # Session arc templates
        if dominant == MeditationState.SETTLING:
            return "A session of arrival. The mind learning to be still."

        elif dominant == MeditationState.FLOW:
            return "A session of movement. Awareness flowed without obstruction."

        elif dominant == MeditationState.DEEP:
            return "A session of depth. Profound stillness was touched."

        elif dominant == MeditationState.LIMINAL:
            return "A session of thresholds. Dancing at the edge of sleep."

        elif dominant == MeditationState.PRESENT:
            return "A session of presence. Simply being, without agenda."

        else:
            return "A session of changes. Many states arose and passed."

    def generate_comfyui_prompt(
        self,
        signature: StateSignature,
        character_awakening: float
    ) -> str:
        """
        Generate visual prompt for ComfyUI/Stable Diffusion

        NOT literal. Evocative. Abstract.
        Based on meditation state and companion awakening.

        Style: Contemplative, minimal, ethereal
        References: Ryoji Ikeda, Bill Viola, James Turrell
        """

        # Base visual themes per state
        state_visuals = {
            MeditationState.SETTLING: [
                "turbulent water surface, ripples forming and dissolving",
                "particles slowly gathering, finding center",
                "fog clearing, revealing darkness beneath",
            ],
            MeditationState.FLOW: [
                "fluid forms in motion, organic curves",
                "water flowing over stone, smooth transitions",
                "light moving through space, shifting patterns",
            ],
            MeditationState.DEEP: [
                "profound darkness with subtle gradations",
                "the bottom of the ocean, pressure and silence",
                "void with texture, depth without light",
            ],
            MeditationState.LIMINAL: [
                "threshold between two states, dissolving boundary",
                "dreamlike forms, not quite real",
                "fog and shadow, ambiguous space",
            ],
            MeditationState.PRESENT: [
                "simple geometry, minimal composition",
                "just light and shadow, nothing more",
                "the most ordinary moment, completely ordinary",
            ]
        }

        # Select base visual
        base_visual = random.choice(state_visuals[signature.state])

        # Style modifiers (based on awakening)
        if character_awakening < 0.3:
            style = "minimal, abstract, black and white"
        elif character_awakening < 0.7:
            style = "contemplative abstract, subtle gradations, monochrome with rare color"
        else:
            style = "ethereal, otherworldly, strange beauty, unexpected compositions"

        # Technical parameters
        technical = "high contrast, minimal, contemplative, 8k, fine art photography"

        # Negative prompt (what to avoid)
        negative = "faces, recognizable objects, text, words, kitsch, cliché spiritual imagery, mandalas, lotuses, rainbow colors"

        # Compose prompt
        prompt = f"{base_visual}, {style}, {technical}"

        return {
            'positive': prompt,
            'negative': negative,
            'style': style.split(',')[0]  # Primary style
        }
