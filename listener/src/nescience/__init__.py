"""
NESCIENCE - The Listener as contemplative art companion

Not wellness optimization. Not diagnostic.
Witnessing consciousness without judgment.

Based on:
- Vipassana meditation (S.N. Goenka tradition)
- Anicca (अनिच्च) - impermanence
- Tsukumogami (付喪神) - objects gaining souls through use
- Nescience - embracing not-knowing
"""

from .meditation_states import MeditationStateClassifier, MeditationState
from .character_evolution import CharacterState, CharacterEvolution
from .poetic_interpreter import PoeticInterpreter

__all__ = [
    'MeditationStateClassifier',
    'MeditationState',
    'CharacterState',
    'CharacterEvolution',
    'PoeticInterpreter'
]
