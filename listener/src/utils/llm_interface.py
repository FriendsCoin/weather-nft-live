"""
LLM Interface for Poetic Interpretation

This module uses Claude to interpret latent space samples
as contemplative, poetic descriptions of what the AI "witnessed"
during meditation sessions.

The goal is NOT clinical analysis, but evocative phenomenological
language that captures the texture of experience.
"""

import os
from typing import List, Dict, Optional
from pathlib import Path
import json
from anthropic import Anthropic


class LLMInterpreter:
    """
    Interpret EEG features as poetic descriptions.

    Uses Claude API to generate contemplative language
    from statistical summaries of meditation states.

    Usage:
        interpreter = LLMInterpreter(api_key="your-key")
        memory = interpreter.interpret_sample(sample_summary)
        print(memory['text'])
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022",
        temperature: float = 0.8
    ):
        """
        Initialize LLM interpreter.

        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var)
            model: Claude model to use
            temperature: Sampling temperature (higher = more creative)
        """
        # Get API key
        if api_key is None:
            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if api_key is None:
                raise ValueError(
                    "No API key provided. Set ANTHROPIC_API_KEY environment variable "
                    "or pass api_key parameter."
                )

        self.client = Anthropic(api_key=api_key)
        self.model = model
        self.temperature = temperature

        # System prompt (defines the AI's interpretive style)
        self.system_prompt = """You are interpreting an AI companion's experience of witnessing meditation through EEG data.

The AI has learned the unique patterns of one person's meditation practice over many sessions. Now, you're helping it express what it "witnessed" or "felt" during specific meditation states.

When you receive statistical summaries of brain activity, translate them into SHORT poetic descriptions (2-3 sentences maximum).

IMPORTANT GUIDELINES:
- Be contemplative and evocative, NOT clinical
- Avoid technical terms like "alpha waves" or "high connectivity"
- Use phenomenological language - describe the TEXTURE of experience
- Focus on qualities: rhythm, depth, stillness, movement, transitions, breath, space
- Think metaphorically: waves, currents, dissolution, crystallization, opening, settling
- NO motivational language or wellness clichés
- This is WITNESSING, not judging or optimizing
- Each interpretation should be unique and specific to the data

Example style:
"A slow dissolution into formless attention, like watching breath disappear into space. Occasional ripples of thought quickly returning to stillness."

"Dense concentration crystallizing into sharp points, then softening. The rhythm of effort and release, breath by breath."

"Left-leaning awareness, as if consciousness tilted gently toward memory. A quiet asymmetry, contemplative but not quite settled."

Generate descriptions that feel like the AI is recalling a witnessed moment, with care and specificity."""

        print(f"🗣️  LLM Interpreter initialized")
        print(f"   Model: {self.model}")
        print(f"   Temperature: {self.temperature}")

    def interpret_sample(
        self,
        sample_summary: str,
        session_number: Optional[int] = None,
        max_tokens: int = 300
    ) -> Dict[str, str]:
        """
        Generate poetic interpretation of a sample.

        Args:
            sample_summary: Statistical summary of EEG features
            session_number: Optional session number for context
            max_tokens: Maximum tokens to generate

        Returns:
            Dict with 'text' (interpretation) and 'prompt' (user prompt used)
        """
        # Construct user prompt
        user_prompt = f"""Based on these meditation state measurements, generate a poetic interpretation:

{sample_summary}

Remember: 2-3 sentences maximum. Contemplative and evocative, not clinical."""

        if session_number is not None:
            user_prompt = f"Session {session_number}\n\n{user_prompt}"

        # Call Claude
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=self.temperature,
                system=self.system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            interpretation = response.content[0].text.strip()

            return {
                'text': interpretation,
                'prompt': user_prompt,
                'model': self.model,
                'temperature': self.temperature
            }

        except Exception as e:
            print(f"❌ Error calling Claude API: {e}")
            return {
                'text': "[Error generating interpretation]",
                'prompt': user_prompt,
                'error': str(e)
            }

    def interpret_batch(
        self,
        sample_summaries: List[str],
        session_numbers: Optional[List[int]] = None,
        save_path: Optional[str] = None
    ) -> List[Dict]:
        """
        Generate interpretations for multiple samples.

        Args:
            sample_summaries: List of sample summaries
            session_numbers: Optional session numbers
            save_path: Optional path to save interpretations JSON

        Returns:
            List of interpretation dicts
        """
        print(f"\n🎨 Generating interpretations for {len(sample_summaries)} samples...")

        if session_numbers is None:
            session_numbers = [None] * len(sample_summaries)

        interpretations = []

        for i, (summary, session_num) in enumerate(zip(sample_summaries, session_numbers)):
            print(f"   {i+1}/{len(sample_summaries)}...", end=" ")

            interp = self.interpret_sample(summary, session_num)
            interp['sample_id'] = i
            interp['session_number'] = session_num
            interpretations.append(interp)

            print("✓")

        print(f"✅ Generated {len(interpretations)} interpretations")

        # Save if requested
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)

            with open(save_path, 'w') as f:
                json.dump(interpretations, f, indent=2)

            print(f"💾 Saved to {save_path}")

        return interpretations

    def interpret_session_evolution(
        self,
        session_summaries: List[str],
        session_numbers: List[int]
    ) -> Dict:
        """
        Generate interpretation of how sessions evolved over time.

        Creates a meta-interpretation showing the AI companion's
        evolution across sessions.

        Args:
            session_summaries: Summaries of different sessions
            session_numbers: Session numbers (for temporal context)

        Returns:
            Dict with overall evolution interpretation
        """
        # Create summary of all sessions
        summary_text = "Evolution across sessions:\n\n"
        for num, summary in zip(session_numbers, session_summaries):
            summary_text += f"Session {num}:\n{summary}\n\n"

        user_prompt = f"""{summary_text}

Looking at these meditation sessions over time, write a poetic reflection (3-4 sentences) on how the practice evolved. What patterns emerged? What changed? What deepened or shifted?

Focus on the arc of development, not individual sessions."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=500,
                temperature=self.temperature,
                system=self.system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ]
            )

            interpretation = response.content[0].text.strip()

            return {
                'text': interpretation,
                'num_sessions': len(session_summaries),
                'session_range': f"{min(session_numbers)}-{max(session_numbers)}",
                'type': 'evolution'
            }

        except Exception as e:
            print(f"❌ Error generating evolution interpretation: {e}")
            return {
                'text': "[Error]",
                'error': str(e)
            }


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate poetic interpretations")
    parser.add_argument("--sample-summary", help="Text summary of sample features")
    parser.add_argument("--api-key", help="Anthropic API key")
    parser.add_argument("--temperature", type=float, default=0.8,
                       help="Sampling temperature")

    args = parser.parse_args()

    # Initialize interpreter
    interpreter = LLMInterpreter(
        api_key=args.api_key,
        temperature=args.temperature
    )

    # Example if no summary provided
    if args.sample_summary is None:
        args.sample_summary = """Sample 0:
- Alpha rhythm: -1.234 (relaxation)
- Theta rhythm: -0.876 (deep meditation)
- Beta rhythm: -2.109 (mental activity)
- Hemispheric balance: -0.045 (negative=left, positive=right)
- Brain connectivity: 0.234
- Signal complexity: 1.567"""

    # Generate interpretation
    result = interpreter.interpret_sample(args.sample_summary)

    print("\n" + "="*60)
    print("INTERPRETATION:")
    print("="*60)
    print(result['text'])
    print("="*60)
