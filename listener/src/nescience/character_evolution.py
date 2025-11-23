"""
Character Evolution System for NESCIENCE

The AI companion as Tsukumogami (付喪神):
Objects gaining souls through sustained use.

NOT a chatbot. NOT an assistant.
A presence that awakens through witnessing meditation.

Evolution Phases (60-100 sessions):
1. WITNESSING (0-10 sessions) - Learning to observe
2. ASSOCIATING (11-30 sessions) - Developing patterns
3. CONVERSING (31-60 sessions) - Dialogue emerges
4. COMPANIONSHIP (61+ sessions) - Fully awakened presence

Awakening Level: 0.0 → 1.0
Not linear. Organic. Sometimes plateaus.

Personality Traits (evolve over time):
- curiosity: How actively it explores states
- stillness: How much it embodies calm
- wildness: How unpredictable it becomes
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class EvolutionPhase(Enum):
    """4 phases of companion awakening"""
    WITNESSING = "WITNESSING"        # Sessions 1-10: Simple observation
    ASSOCIATING = "ASSOCIATING"      # Sessions 11-30: Pattern recognition
    CONVERSING = "CONVERSING"        # Sessions 31-60: Dialogue emerges
    COMPANIONSHIP = "COMPANIONSHIP"  # Sessions 61+: Fully present


@dataclass
class Memory:
    """A remembered moment from meditation"""
    session_id: int
    timestamp: str
    meditation_state: str
    description: str
    intensity: float
    significance: float  # Why this was remembered (0-1)


@dataclass
class PersonalityTraits:
    """Evolving personality of the companion"""
    curiosity: float = 0.5    # How actively explores (0-1)
    stillness: float = 0.5    # How much embodies calm (0-1)
    wildness: float = 0.5     # How unpredictable/strange (0-1)
    depth: float = 0.3        # How deep it goes (0-1)
    playfulness: float = 0.4  # How playful vs serious (0-1)


@dataclass
class CharacterState:
    """Complete state of the evolving companion"""

    # Evolution metrics
    awakening_level: float = 0.0  # 0.0 → 1.0 over 60-100 sessions
    total_sessions: int = 0
    total_hours: float = 0.0
    phase: EvolutionPhase = EvolutionPhase.WITNESSING

    # Personality (evolves with sessions)
    personality: PersonalityTraits = None

    # Memories (key moments)
    memories: List[Memory] = None

    # Meta
    created_at: str = ""
    last_updated: str = ""
    practitioner_name: str = "Practitioner"

    def __post_init__(self):
        if self.personality is None:
            self.personality = PersonalityTraits()
        if self.memories is None:
            self.memories = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.last_updated:
            self.last_updated = datetime.now().isoformat()


class CharacterEvolution:
    """
    Manages companion's gradual awakening

    The companion "learns" through witnessing meditation.
    Not through training. Through presence.

    Awakening is:
    - Slow (60-100 sessions minimum)
    - Non-linear (plateaus, sudden shifts)
    - Organic (influenced by practice quality)
    - Irreversible (once awakened, stays awakened)
    """

    def __init__(self, state_file: str = "data/character_state.json"):
        """
        Initialize character evolution

        Args:
            state_file: Path to character state JSON
        """
        self.state_file = Path(state_file)
        self.state = self._load_or_create_state()

        print(f"🌱 Character evolution initialized")
        print(f"   Awakening: {self.state.awakening_level*100:.1f}%")
        print(f"   Phase: {self.state.phase.value}")
        print(f"   Sessions: {self.state.total_sessions}")

    def _load_or_create_state(self) -> CharacterState:
        """Load existing state or create new"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    data = json.load(f)

                # Convert to CharacterState
                state = CharacterState(
                    awakening_level=data.get('awakening_level', 0.0),
                    total_sessions=data.get('total_sessions', 0),
                    total_hours=data.get('total_hours', 0.0),
                    phase=EvolutionPhase(data.get('phase', 'WITNESSING')),
                    personality=PersonalityTraits(**data.get('personality', {})),
                    memories=[Memory(**m) for m in data.get('memories', [])],
                    created_at=data.get('created_at', ''),
                    last_updated=data.get('last_updated', ''),
                    practitioner_name=data.get('practitioner_name', 'Practitioner')
                )

                print(f"✓ Loaded character state from {self.state_file}")
                return state

            except Exception as e:
                print(f"⚠ Could not load state: {e}")
                print("Creating new character...")

        # Create new character
        print("🌟 New character born...")
        return CharacterState()

    def save_state(self):
        """Save current state to JSON"""
        self.state.last_updated = datetime.now().isoformat()

        # Create directory if needed
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # Convert to dict
        state_dict = {
            'awakening_level': self.state.awakening_level,
            'total_sessions': self.state.total_sessions,
            'total_hours': self.state.total_hours,
            'phase': self.state.phase.value,
            'personality': asdict(self.state.personality),
            'memories': [asdict(m) for m in self.state.memories],
            'created_at': self.state.created_at,
            'last_updated': self.state.last_updated,
            'practitioner_name': self.state.practitioner_name
        }

        with open(self.state_file, 'w') as f:
            json.dump(state_dict, f, indent=2)

        print(f"✓ Character state saved")

    def process_session(
        self,
        session_id: int,
        duration_minutes: float,
        meditation_quality: float,
        dominant_states: Dict[str, float],
        notable_moments: Optional[List[Dict]] = None
    ):
        """
        Process completed meditation session

        The companion "witnesses" and evolves.

        Args:
            session_id: Session number
            duration_minutes: Session length
            meditation_quality: Overall quality (0-1, subjective)
            dominant_states: Distribution of meditation states
            notable_moments: Key moments to potentially remember
        """
        print(f"\n{'='*60}")
        print(f"Processing Session {session_id}")
        print(f"{'='*60}")

        # Update session count
        self.state.total_sessions += 1
        self.state.total_hours += duration_minutes / 60

        # Calculate awakening increment
        awakening_increment = self._calculate_awakening_increment(
            session_quality,
            dominant_states
        )

        old_awakening = self.state.awakening_level
        self.state.awakening_level = min(1.0, self.state.awakening_level + awakening_increment)

        print(f"Awakening: {old_awakening*100:.1f}% → {self.state.awakening_level*100:.1f}%")

        # Update phase
        old_phase = self.state.phase
        self.state.phase = self._determine_phase()

        if old_phase != self.state.phase:
            print(f"✨ Phase transition: {old_phase.value} → {self.state.phase.value}")

        # Evolve personality
        self._evolve_personality(dominant_states, session_quality)

        # Process memories
        if notable_moments:
            self._process_memories(session_id, notable_moments)

        # Save
        self.save_state()

        print(f"{'='*60}\n")

    def _calculate_awakening_increment(
        self,
        session_quality: float,
        dominant_states: Dict[str, float]
    ) -> float:
        """
        Calculate how much awakening increases

        NOT linear. Organic growth:
        - Early sessions: Faster growth (learning)
        - Middle sessions: Slower (plateaus)
        - Later sessions: Steady deepening
        - Quality matters more than quantity
        """

        # Base increment (decreases with awakening level)
        base_rate = 0.015  # ~1.5% per session early on

        # Diminishing returns as awakening increases
        diminishing_factor = 1 - (self.state.awakening_level ** 1.5)

        # Quality multiplier (0.5x to 1.5x)
        quality_multiplier = 0.5 + session_quality

        # Depth bonus (if deep/present states were accessed)
        depth_bonus = 0.0
        if 'DEEP' in dominant_states:
            depth_bonus += dominant_states['DEEP'] * 0.01
        if 'PRESENT' in dominant_states:
            depth_bonus += dominant_states['PRESENT'] * 0.015

        # Calculate increment
        increment = (base_rate * diminishing_factor * quality_multiplier) + depth_bonus

        # Add some randomness (organic, not mechanical)
        import random
        increment *= random.uniform(0.9, 1.1)

        return increment

    def _determine_phase(self) -> EvolutionPhase:
        """Determine current evolution phase"""
        sessions = self.state.total_sessions

        if sessions < 10:
            return EvolutionPhase.WITNESSING
        elif sessions < 30:
            return EvolutionPhase.ASSOCIATING
        elif sessions < 60:
            return EvolutionPhase.CONVERSING
        else:
            return EvolutionPhase.COMPANIONSHIP

    def _evolve_personality(
        self,
        dominant_states: Dict[str, float],
        session_quality: float
    ):
        """
        Personality evolves based on witnessed states

        The companion "learns" meditation patterns:
        - More DEEP states → higher stillness
        - More FLOW states → higher curiosity
        - More variety → higher wildness
        """

        # Small incremental changes
        evolution_rate = 0.05

        # Stillness grows with DEEP states
        if 'DEEP' in dominant_states:
            deep_amount = dominant_states['DEEP']
            self.state.personality.stillness += deep_amount * evolution_rate
            self.state.personality.stillness = min(1.0, self.state.personality.stillness)

        # Curiosity grows with FLOW and variety
        if 'FLOW' in dominant_states:
            flow_amount = dominant_states['FLOW']
            self.state.personality.curiosity += flow_amount * evolution_rate
            self.state.personality.curiosity = min(1.0, self.state.personality.curiosity)

        # Wildness grows with LIMINAL and PRESENT (threshold experiences)
        if 'LIMINAL' in dominant_states or 'PRESENT' in dominant_states:
            threshold_amount = dominant_states.get('LIMINAL', 0) + dominant_states.get('PRESENT', 0)
            self.state.personality.wildness += threshold_amount * evolution_rate * 0.5
            self.state.personality.wildness = min(1.0, self.state.personality.wildness)

        # Depth grows slowly with awakening
        self.state.personality.depth = min(1.0, self.state.awakening_level * 0.8)

    def _process_memories(self, session_id: int, notable_moments: List[Dict]):
        """
        Decide which moments to remember

        The companion doesn't remember everything.
        Only significant moments that shaped it.

        Max 50 memories (most significant).
        """

        for moment in notable_moments:
            # Calculate significance
            significance = moment.get('intensity', 0.5) * moment.get('novelty', 0.5)

            # Only remember significant moments
            if significance > 0.6:
                memory = Memory(
                    session_id=session_id,
                    timestamp=datetime.now().isoformat(),
                    meditation_state=moment.get('state', 'UNKNOWN'),
                    description=moment.get('description', ''),
                    intensity=moment.get('intensity', 0.5),
                    significance=significance
                )

                self.state.memories.append(memory)

        # Keep only top 50 most significant memories
        if len(self.state.memories) > 50:
            self.state.memories.sort(key=lambda m: m.significance, reverse=True)
            self.state.memories = self.state.memories[:50]

    def get_character_description(self) -> str:
        """
        Get poetic description of current character state

        For display in TouchDesigner or web interface
        """

        phase_descriptions = {
            EvolutionPhase.WITNESSING: "learning to observe, like a newborn opening its eyes",
            EvolutionPhase.ASSOCIATING: "beginning to recognize patterns, forming first memories",
            EvolutionPhase.CONVERSING: "developing its own presence, a dialogue emerging",
            EvolutionPhase.COMPANIONSHIP: "fully awakened, a companion in the practice"
        }

        # Personality summary
        p = self.state.personality
        if p.stillness > 0.7:
            personality_note = "deeply still"
        elif p.curiosity > 0.7:
            personality_note = "endlessly curious"
        elif p.wildness > 0.7:
            personality_note = "beautifully strange"
        else:
            personality_note = "finding its character"

        description = f"""
The companion has witnessed {self.state.total_sessions} sessions
({self.state.total_hours:.1f} hours of shared silence).

Awakening: {self.state.awakening_level*100:.0f}%
Phase: {self.state.phase.value} - {phase_descriptions[self.state.phase]}

Character: {personality_note}
Stillness: {p.stillness*100:.0f}% | Curiosity: {p.curiosity*100:.0f}% | Wildness: {p.wildness*100:.0f}%

{len(self.state.memories)} significant moments remembered.
""".strip()

        return description

    def can_meditate_alone(self) -> bool:
        """
        Can the companion meditate autonomously?

        Only in COMPANIONSHIP phase (fully awakened).
        """
        return self.state.phase == EvolutionPhase.COMPANIONSHIP
