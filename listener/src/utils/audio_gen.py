"""
Audio/Voice Generation for THE LISTENER

Generate contemplative voice narration for meditation interpretations:
- Coqui TTS for natural voice synthesis
- Multiple voice styles (calm, whispered, meditative)
- Audio effects (reverb, slow tempo)
- Combine with video for complete multimedia memories

The AI companion's voice emerges from learned meditation states.
"""

import numpy as np
from pathlib import Path
from typing import List, Optional, Dict, Tuple
import json

try:
    from TTS.api import TTS
    COQUI_AVAILABLE = True
except ImportError:
    COQUI_AVAILABLE = False
    print("⚠️  Coqui TTS not installed. Install with: pip install TTS")

try:
    import soundfile as sf
    SOUNDFILE_AVAILABLE = True
except ImportError:
    SOUNDFILE_AVAILABLE = False
    print("⚠️  soundfile not installed. Install with: pip install soundfile")

try:
    import scipy.signal as signal
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False


class VoiceGenerator:
    """
    Generate contemplative voice narration from text interpretations.

    Uses Coqui TTS with post-processing for meditative quality:
    - Slower speaking rate
    - Reverb/echo effects
    - Calm, whispering voices
    - Pauses and breath

    Usage:
        generator = VoiceGenerator()

        # Generate single narration
        audio_path = generator.generate_voice(
            text="Waves of stillness dissolving into formless attention",
            voice_style="calm"
        )

        # Combine with video
        video_with_audio = generator.add_voice_to_video(
            video_path="meditation.mp4",
            text="Deep concentration crystallizing into sharp points"
        )
    """

    def __init__(
        self,
        output_dir: str = "data/outputs/audio",
        sample_rate: int = 22050
    ):
        """
        Initialize voice generator.

        Args:
            output_dir: Directory to save audio files
            sample_rate: Audio sample rate (Hz)
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.sample_rate = sample_rate
        self.tts = None

        print(f"🎙️  Voice Generator initialized")
        print(f"   Output: {self.output_dir}")
        print(f"   Sample rate: {self.sample_rate} Hz")

        # Initialize TTS
        self._init_tts()

    def _init_tts(self):
        """Initialize Coqui TTS model."""
        if not COQUI_AVAILABLE:
            print("❌ Coqui TTS not available")
            return

        try:
            # Use XTTS v2 for high quality multi-lingual voice
            # or "tts_models/en/ljspeech/tacotron2-DDC" for faster generation
            model_name = "tts_models/en/vctk/vits"  # Multiple voices available

            print(f"   Loading TTS model: {model_name}...")
            self.tts = TTS(model_name=model_name)

            print(f"✅ TTS model loaded")

            # List available speakers
            if hasattr(self.tts, 'speakers') and self.tts.speakers:
                print(f"   Available voices: {len(self.tts.speakers)}")

        except Exception as e:
            print(f"⚠️  Could not load TTS model: {e}")
            self.tts = None

    def generate_voice(
        self,
        text: str,
        voice_style: str = "calm",
        speaker: Optional[str] = None,
        output_name: Optional[str] = None,
        add_effects: bool = True
    ) -> Optional[Path]:
        """
        Generate voice narration from text.

        Args:
            text: Text to narrate
            voice_style: "calm", "whispered", "deep"
            speaker: Specific speaker ID (if model supports it)
            output_name: Custom output filename
            add_effects: Apply reverb/slow effects

        Returns:
            Path to generated audio file
        """
        if self.tts is None:
            print("❌ TTS not initialized")
            return None

        if not SOUNDFILE_AVAILABLE:
            print("❌ soundfile required for audio export")
            return None

        print(f"\n🎙️  Generating voice...")
        print(f"   Text: {text[:60]}...")
        print(f"   Style: {voice_style}")

        # Select speaker based on style
        if speaker is None:
            speaker = self._select_speaker_for_style(voice_style)

        # Generate audio
        try:
            # Generate to temporary WAV
            temp_path = self.output_dir / "temp_tts.wav"

            if hasattr(self.tts, 'speakers') and speaker:
                self.tts.tts_to_file(
                    text=text,
                    speaker=speaker,
                    file_path=str(temp_path)
                )
            else:
                self.tts.tts_to_file(
                    text=text,
                    file_path=str(temp_path)
                )

            # Load audio
            audio, sr = sf.read(temp_path)

            # Apply effects if requested
            if add_effects:
                audio = self._apply_meditation_effects(audio, sr, voice_style)

            # Generate output filename
            if output_name is None:
                output_name = f"voice_{voice_style}.wav"

            output_path = self.output_dir / output_name

            # Save processed audio
            sf.write(output_path, audio, self.sample_rate)

            # Cleanup temp
            temp_path.unlink()

            print(f"✅ Voice generated: {output_path}")
            print(f"   Duration: {len(audio) / self.sample_rate:.2f}s")

            return output_path

        except Exception as e:
            print(f"❌ Error generating voice: {e}")
            return None

    def _select_speaker_for_style(self, voice_style: str) -> Optional[str]:
        """Select appropriate speaker for voice style."""
        if not hasattr(self.tts, 'speakers') or not self.tts.speakers:
            return None

        # Map styles to speaker preferences
        # VCTK dataset has speakers like "p225", "p226", etc.
        style_preferences = {
            "calm": ["p225", "p228", "p229"],      # Female, calm voices
            "whispered": ["p226", "p227"],         # Softer voices
            "deep": ["p245", "p246", "p247"],      # Male, deeper voices
        }

        preferences = style_preferences.get(voice_style, style_preferences["calm"])

        # Find first available preferred speaker
        for pref in preferences:
            if pref in self.tts.speakers:
                return pref

        # Default to first speaker
        return self.tts.speakers[0] if self.tts.speakers else None

    def _apply_meditation_effects(
        self,
        audio: np.ndarray,
        sr: int,
        style: str
    ) -> np.ndarray:
        """
        Apply audio effects for meditative quality.

        Effects:
        - Time stretching (slower, more contemplative)
        - Reverb (spaciousness)
        - Low-pass filter (warmth)
        - Gentle fade in/out
        """
        if not SCIPY_AVAILABLE:
            return audio

        # 1. Slow down (time stretch)
        slowdown_factor = {
            "calm": 0.9,       # 10% slower
            "whispered": 0.85, # 15% slower
            "deep": 0.88       # 12% slower
        }.get(style, 0.9)

        audio_slow = self._time_stretch(audio, slowdown_factor)

        # 2. Add gentle reverb
        audio_reverb = self._add_reverb(audio_slow, sr, decay=0.3)

        # 3. Low-pass filter (remove harsh high frequencies)
        audio_warm = self._lowpass_filter(audio_reverb, sr, cutoff=8000)

        # 4. Fade in/out
        audio_faded = self._apply_fade(audio_warm, sr, fade_duration=0.5)

        # 5. Normalize
        audio_final = audio_faded / np.max(np.abs(audio_faded)) * 0.95

        return audio_final

    def _time_stretch(self, audio: np.ndarray, factor: float) -> np.ndarray:
        """Simple time stretching using resampling."""
        # This is a simple approach - for better quality, use librosa
        target_length = int(len(audio) / factor)
        indices = np.linspace(0, len(audio) - 1, target_length)
        stretched = np.interp(indices, np.arange(len(audio)), audio)
        return stretched

    def _add_reverb(self, audio: np.ndarray, sr: int, decay: float = 0.3) -> np.ndarray:
        """Add simple reverb effect."""
        # Create impulse response (simplified)
        ir_length = int(sr * 0.5)  # 0.5 second reverb
        ir = np.zeros(ir_length)

        # Add echoes at different delays
        delays = [int(sr * d) for d in [0.05, 0.1, 0.15, 0.25, 0.4]]
        for i, delay in enumerate(delays):
            if delay < ir_length:
                ir[delay] = decay ** (i + 1)

        # Convolve
        reverbed = np.convolve(audio, ir, mode='same')

        # Mix with original (50/50)
        mixed = 0.5 * audio + 0.5 * reverbed

        return mixed

    def _lowpass_filter(self, audio: np.ndarray, sr: int, cutoff: int = 8000) -> np.ndarray:
        """Apply low-pass filter for warmth."""
        nyquist = sr // 2
        normalized_cutoff = cutoff / nyquist

        # Design butterworth filter
        b, a = signal.butter(4, normalized_cutoff, btype='low')

        # Apply filter
        filtered = signal.filtfilt(b, a, audio)

        return filtered

    def _apply_fade(self, audio: np.ndarray, sr: int, fade_duration: float = 0.5) -> np.ndarray:
        """Apply fade in/out."""
        fade_samples = int(fade_duration * sr)

        # Fade in
        fade_in = np.linspace(0, 1, fade_samples)
        audio[:fade_samples] *= fade_in

        # Fade out
        fade_out = np.linspace(1, 0, fade_samples)
        audio[-fade_samples:] *= fade_out

        return audio

    def add_voice_to_video(
        self,
        video_path: str,
        text: Optional[str] = None,
        audio_path: Optional[str] = None,
        voice_style: str = "calm",
        output_name: Optional[str] = None
    ) -> Optional[Path]:
        """
        Add voice narration to video.

        Args:
            video_path: Path to video file
            text: Text to narrate (will generate audio)
            audio_path: Pre-generated audio file (alternative to text)
            voice_style: Voice style if generating from text
            output_name: Custom output filename

        Returns:
            Path to video with audio
        """
        try:
            import subprocess

            print(f"\n🎬 Adding voice to video...")

            # Generate audio if text provided
            if text and not audio_path:
                audio_path = self.generate_voice(
                    text=text,
                    voice_style=voice_style,
                    output_name="temp_narration.wav"
                )

            if not audio_path:
                print("❌ No audio provided")
                return None

            # Generate output filename
            if output_name is None:
                video_name = Path(video_path).stem
                output_name = f"{video_name}_with_voice.mp4"

            output_path = self.output_dir.parent / "videos" / output_name

            # Use ffmpeg to combine
            cmd = [
                "ffmpeg",
                "-i", str(video_path),
                "-i", str(audio_path),
                "-c:v", "copy",
                "-c:a", "aac",
                "-shortest",  # Match shortest duration
                "-y",  # Overwrite
                str(output_path)
            ]

            subprocess.run(cmd, check=True, capture_output=True)

            print(f"✅ Video with voice created: {output_path}")
            return output_path

        except subprocess.CalledProcessError as e:
            print(f"❌ FFmpeg error: {e.stderr.decode() if e.stderr else e}")
            return None
        except Exception as e:
            print(f"❌ Error adding voice: {e}")
            return None

    def create_ambient_soundscape(
        self,
        duration: float = 60.0,
        soundscape_type: str = "breathing",
        output_name: Optional[str] = None
    ) -> Optional[Path]:
        """
        Create ambient soundscape for meditation videos.

        Args:
            duration: Duration in seconds
            soundscape_type: "breathing", "waves", "silence"
            output_name: Custom output filename

        Returns:
            Path to generated soundscape
        """
        if not SOUNDFILE_AVAILABLE:
            print("❌ soundfile required")
            return None

        print(f"\n🌊 Creating ambient soundscape...")
        print(f"   Type: {soundscape_type}")
        print(f"   Duration: {duration}s")

        # Generate samples
        n_samples = int(duration * self.sample_rate)
        audio = np.zeros(n_samples)

        if soundscape_type == "breathing":
            # Create breathing rhythm (slow sine wave)
            t = np.linspace(0, duration, n_samples)
            breath_rate = 0.15  # 0.15 Hz = ~6 second breath cycle

            # Breath sound (filtered noise with breathing envelope)
            noise = np.random.randn(n_samples) * 0.1
            envelope = 0.5 + 0.5 * np.sin(2 * np.pi * breath_rate * t)

            audio = noise * envelope

            # Low-pass filter for warmth
            audio = self._lowpass_filter(audio, self.sample_rate, cutoff=2000)

        elif soundscape_type == "waves":
            # Ocean-like waves (multiple frequencies)
            t = np.linspace(0, duration, n_samples)

            for freq in [0.05, 0.08, 0.12]:  # Different wave periods
                amplitude = np.random.uniform(0.2, 0.4)
                audio += amplitude * np.sin(2 * np.pi * freq * t)

            # Add noise for texture
            audio += np.random.randn(n_samples) * 0.05

        elif soundscape_type == "silence":
            # Very quiet noise floor
            audio = np.random.randn(n_samples) * 0.001

        # Normalize
        audio = audio / np.max(np.abs(audio)) * 0.5

        # Add subtle reverb
        audio = self._add_reverb(audio, self.sample_rate, decay=0.4)

        # Generate output filename
        if output_name is None:
            output_name = f"ambient_{soundscape_type}.wav"

        output_path = self.output_dir / output_name

        # Save
        sf.write(output_path, audio, self.sample_rate)

        print(f"✅ Ambient soundscape created: {output_path}")

        return output_path


# CLI interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate meditation audio")
    parser.add_argument("--mode", choices=["voice", "ambient"],
                       required=True, help="Generation mode")
    parser.add_argument("--text", help="Text for voice generation")
    parser.add_argument("--style", default="calm",
                       choices=["calm", "whispered", "deep"],
                       help="Voice style")
    parser.add_argument("--soundscape", default="breathing",
                       choices=["breathing", "waves", "silence"],
                       help="Ambient soundscape type")
    parser.add_argument("--duration", type=float, default=60.0,
                       help="Duration for ambient")
    parser.add_argument("--output", help="Output filename")

    args = parser.parse_args()

    generator = VoiceGenerator()

    if args.mode == "voice":
        if not args.text:
            print("❌ --text required for voice mode")
        else:
            generator.generate_voice(
                text=args.text,
                voice_style=args.style,
                output_name=args.output
            )

    elif args.mode == "ambient":
        generator.create_ambient_soundscape(
            duration=args.duration,
            soundscape_type=args.soundscape,
            output_name=args.output
        )
