"""
TRIDENT Bio-Acoustic Feature Extraction Module (Layer 3)

Implements the bio-acoustic distress detection layer as specified in PRD Section 4.4.
Extracts vocal stress indicators from audio to provide parallel signal path when ASR fails.

Key Features:
- Pitch (F0) extraction using pYIN algorithm
- RMS energy computation
- Jitter calculation (pitch perturbation)
- Sex-adaptive distress scoring

Formula (from PRD Section 4.4.2):
    D = 0.30 * P + 0.35 * V + 0.20 * E + 0.15 * J

    Where:
        P = Pitch elevation (sex-adaptive baseline)
        V = Pitch instability (coefficient of variation)
        E = Energy (RMS normalized)
        J = Jitter (cycle-to-cycle F0 variation)
"""

import librosa
import numpy as np
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BioAcousticProcessor:
    """
    Processes audio to extract bio-acoustic features indicative of vocal distress.

    Uses librosa for feature extraction and implements the sex-adaptive distress
    scoring algorithm from the TRIDENT PRD.
    """

    def __init__(self, sample_rate: int = 16000):
        """
        Initialize the bio-acoustic processor.

        Args:
            sample_rate: Target sampling rate for audio (default: 16000 Hz for Whisper compatibility)
        """
        self.sample_rate = sample_rate
        self.f0_range = (50, 400)  # Hz - typical human vocal range

    def extract_features(self, audio_path: str) -> Dict[str, float]:
        """
        Extract bio-acoustic features from audio file.

        Args:
            audio_path: Path to audio file

        Returns:
            Dictionary containing:
                - f0_mean: Mean fundamental frequency (Hz)
                - f0_cv: Coefficient of variation of F0
                - pitch_elevation: Normalized pitch elevation score (0-1)
                - instability: Normalized pitch instability score (0-1)
                - energy: Normalized RMS energy score (0-1)
                - jitter: Normalized jitter score (0-1)
                - distress_score: Composite distress score (0-1)
        """
        try:
            # Load audio
            y, sr = librosa.load(audio_path, sr=self.sample_rate)
            logger.info(f"Loaded audio: {len(y)/sr:.2f}s duration at {sr}Hz")

            # Extract F0 (fundamental frequency) using pYIN
            f0, voiced_flag, voiced_probs = librosa.pyin(
                y,
                fmin=self.f0_range[0],
                fmax=self.f0_range[1],
                sr=sr
            )

            # Filter to voiced frames only
            f0_voiced = f0[voiced_flag]

            if len(f0_voiced) == 0:
                logger.warning("No voiced frames detected - returning zero distress")
                return self._zero_features()

            # Compute F0 statistics
            f0_mean = np.mean(f0_voiced)
            f0_std = np.std(f0_voiced)
            f0_cv = f0_std / f0_mean if f0_mean > 0 else 0

            # Sex-adaptive pitch elevation (P component)
            # From PRD: Male (F0 < 165Hz): P = (F0 - 120) / 80
            #           Female (F0 >= 165Hz): P = (F0 - 200) / 100
            if f0_mean < 165:
                # Estimated male speaker
                pitch_elevation = (f0_mean - 120) / 80
            else:
                # Estimated female speaker
                pitch_elevation = (f0_mean - 200) / 100

            pitch_elevation = min(1.0, max(0.0, pitch_elevation))

            # Pitch instability (V component)
            # Normalize CV by expected maximum (0.5 for extreme instability)
            instability = min(1.0, f0_cv / 0.5)

            # Energy (E component)
            # Extract RMS energy and normalize
            rms = librosa.feature.rms(y=y)[0]
            rms_mean = np.mean(rms)
            # Normalize by typical maximum (0.1 for very loud)
            energy = min(1.0, rms_mean / 0.1)

            # Jitter (J component)
            # Cycle-to-cycle F0 variation (perturbation)
            if len(f0_voiced) > 1:
                f0_diffs = np.abs(np.diff(f0_voiced))
                jitter_raw = np.mean(f0_diffs) / f0_mean
                # Normalize by typical maximum (0.02 for high perturbation)
                jitter = min(1.0, jitter_raw / 0.02)
            else:
                jitter = 0.0

            # Composite distress score (D)
            # From PRD: D = 0.30*P + 0.35*V + 0.20*E + 0.15*J
            distress_score = (
                0.30 * pitch_elevation +
                0.35 * instability +
                0.20 * energy +
                0.15 * jitter
            )

            logger.info(f"Bio-acoustic features extracted: "
                       f"F0={f0_mean:.1f}Hz, CV={f0_cv:.3f}, "
                       f"Distress={distress_score:.3f}")

            return {
                "f0_mean": float(f0_mean),
                "f0_cv": float(f0_cv),
                "pitch_elevation": float(pitch_elevation),
                "instability": float(instability),
                "energy": float(energy),
                "jitter": float(jitter),
                "distress_score": float(distress_score)
            }

        except Exception as e:
            logger.error(f"Error extracting bio-acoustic features: {e}")
            return self._zero_features()

    def _zero_features(self) -> Dict[str, float]:
        """
        Return zero-valued features (fallback for silent/invalid audio).

        Returns:
            Dictionary with all features set to 0.0
        """
        return {
            "f0_mean": 0.0,
            "f0_cv": 0.0,
            "pitch_elevation": 0.0,
            "instability": 0.0,
            "energy": 0.0,
            "jitter": 0.0,
            "distress_score": 0.0
        }


def process_audio(audio_path: str) -> Dict[str, float]:
    """
    Convenience function to process audio file and extract bio-acoustic features.

    Args:
        audio_path: Path to audio file

    Returns:
        Dictionary of bio-acoustic features
    """
    processor = BioAcousticProcessor()
    return processor.extract_features(audio_path)


if __name__ == "__main__":
    # Test with sample audio
    import sys

    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
    else:
        audio_file = "../assets/call_4_panic.wav"

    print(f"\nProcessing: {audio_file}")
    print("-" * 60)

    features = process_audio(audio_file)

    print("\nBio-Acoustic Features:")
    print(f"  F0 Mean:          {features['f0_mean']:.1f} Hz")
    print(f"  F0 CV:            {features['f0_cv']:.3f}")
    print(f"  Pitch Elevation:  {features['pitch_elevation']:.3f}")
    print(f"  Instability:      {features['instability']:.3f}")
    print(f"  Energy:           {features['energy']:.3f}")
    print(f"  Jitter:           {features['jitter']:.3f}")
    print(f"\n  DISTRESS SCORE:   {features['distress_score']:.3f}")
    print(f"  Classification:   {'HIGH DISTRESS' if features['distress_score'] > 0.5 else 'LOW DISTRESS'}")
    print("-" * 60)
