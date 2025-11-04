"""
Audio analyzer module for BPM and key detection using librosa.
"""

import os
import logging
from typing import Tuple
import numpy as np
import librosa

logger = logging.getLogger(__name__)


class AudioAnalyzer:
    """
    Audio analyzer for detecting BPM and musical key from audio files.
    
    Uses librosa for high-quality, modern audio analysis.
    """
    
    def __init__(self, sample_rate: int = 44100, hop_length: int = 512):
        """
        Initialize the audio analyzer.
        
        Args:
            sample_rate: Target sample rate for analysis
            hop_length: Hop length for analysis (smaller = more precise but slower)
        """
        self.sample_rate = sample_rate
        self.hop_length = hop_length
    
    def detect_bpm(self, audio_file: str) -> float:
        """
        Detect BPM (tempo) from an audio file.
        
        Args:
            audio_file: Path to the audio file
            
        Returns:
            Detected BPM value, or 120.0 as fallback
        """
        if not os.path.exists(audio_file):
            logger.error(f"Audio file not found: {audio_file}")
            return 120.0
        
        try:
            return self._detect_bpm_librosa(audio_file)
        except Exception as e:
            logger.error(f"Error detecting BPM: {e}")
            return 120.0
    
    def detect_key(self, audio_file: str) -> str:
        """
        Detect musical key from an audio file.
        
        Args:
            audio_file: Path to the audio file
            
        Returns:
            Detected key (e.g., "Am", "C", "F#"), or "C" as fallback
        """
        if not os.path.exists(audio_file):
            logger.error(f"Audio file not found: {audio_file}")
            return "C"
        
        try:
            return self._detect_key_librosa(audio_file)
        except Exception as e:
            logger.error(f"Error detecting key: {e}")
            return "C"
    
    def analyze(self, audio_file: str) -> Tuple[float, str]:
        """
        Analyze an audio file for both BPM and key.
        
        Args:
            audio_file: Path to the audio file
            
        Returns:
            Tuple of (BPM, key)
        """
        bpm = self.detect_bpm(audio_file)
        key = self.detect_key(audio_file)
        return bpm, key
    
    def _detect_bpm_librosa(self, audio_file: str) -> float:
        """Detect BPM using librosa."""
        # Load audio file
        y, sr = librosa.load(audio_file, sr=self.sample_rate)
        
        # Use librosa's tempo detection - this is more robust than beat tracking
        # Try tempo estimation first (more accurate for overall tempo)
        try:
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr, hop_length=self.hop_length)
            if tempo > 0:
                return float(tempo)
        except Exception as e:
            logger.debug(f"Beat tracking failed: {e}")
        
        # Fallback: use onset-based tempo estimation
        try:
            # Get onset strength
            onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=self.hop_length)
            
            # Estimate tempo from onset strength
            tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr, hop_length=self.hop_length)
            
            if tempo > 0 and len(tempo) > 0:
                return float(tempo[0])
        except Exception as e:
            logger.debug(f"Onset-based tempo detection failed: {e}")
        
        # Final fallback
        return 120.0
    
    def _detect_key_librosa(self, audio_file: str) -> str:
        """Detect key using librosa."""
        # Load audio file
        y, sr = librosa.load(audio_file, sr=self.sample_rate)
        
        # Extract chromagram (chroma feature) - represents pitch class content
        # Try CQT chromagram first (more accurate for harmonic content)
        try:
            chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=self.hop_length)
        except Exception:
            # Fallback to STFT chromagram
            chroma = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=self.hop_length)
        
        # Average chroma values across time to get overall pitch class distribution
        chroma_mean = np.mean(chroma, axis=1)
        
        # Key profiles for major and minor keys (Krumhansl-Schmuckler profiles)
        # These represent how often each pitch class appears in each key
        major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
        minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
        
        # Normalize profiles
        major_profile = major_profile / np.sum(major_profile)
        minor_profile = minor_profile / np.sum(minor_profile)
        
        # Calculate correlation with each key (major and minor)
        key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        correlations = {}
        
        for i, key in enumerate(key_names):
            # Rotate chroma to match key
            rotated_chroma = np.roll(chroma_mean, -i)
            # Correlation with major profile
            major_corr = np.corrcoef(rotated_chroma, major_profile)[0, 1]
            # Correlation with minor profile
            minor_corr = np.corrcoef(rotated_chroma, minor_profile)[0, 1]
            
            correlations[key] = major_corr
            correlations[f"{key}m"] = minor_corr
        
        # Find key with highest correlation
        best_key = max(correlations, key=correlations.get)
        
        return best_key


def analyze_audio(audio_file: str) -> Tuple[float, str]:
    """
    Convenience function to analyze audio file for BPM and key.
    
    Args:
        audio_file: Path to the audio file
        
    Returns:
        Tuple of (BPM, key)
    """
    analyzer = AudioAnalyzer()
    return analyzer.analyze(audio_file)


def generate_filename_with_features(original_filename: str, bpm: float, key: str) -> str:
    """
    Generate a filename with BPM and key information.
    
    Args:
        original_filename: Original filename (with or without extension)
        bpm: Detected BPM value
        key: Detected musical key
        
    Returns:
        New filename with BPM and key info
    """
    # Split filename and extension
    name, ext = os.path.splitext(original_filename)
    
    # Format BPM as integer
    bpm_str = f"{int(round(bpm))}bpm"
    
    # Create new filename
    new_filename = f"{name}_{bpm_str}_{key}{ext}"
    
    return new_filename
