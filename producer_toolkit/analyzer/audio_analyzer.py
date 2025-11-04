"""
Audio analyzer module for BPM and key detection using aubio.
"""

import os
import logging
from typing import Tuple
import numpy as np
import aubio

logger = logging.getLogger(__name__)


class AudioAnalyzer:
    """
    Audio analyzer for detecting BPM and musical key from audio files.
    
    Uses aubio for high-quality analysis.
    """
    
    def __init__(self, sample_rate: int = 44100, hop_size: int = 512):
        """
        Initialize the audio analyzer.
        
        Args:
            sample_rate: Target sample rate for analysis
            hop_size: Hop size for analysis (smaller = more precise but slower)
        """
        self.sample_rate = sample_rate
        self.hop_size = hop_size
    
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
            return self._detect_bpm_aubio(audio_file)
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
            return self._detect_key_aubio(audio_file)
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
    
    def _detect_bpm_aubio(self, audio_file: str) -> float:
        """Detect BPM using aubio."""
        # Load audio file
        src = aubio.source(audio_file, self.sample_rate, self.hop_size)
        
        # Create tempo detector
        tempo = aubio.tempo("default", self.hop_size, self.hop_size, self.sample_rate)
        
        # Process audio in chunks
        tempo_values = []
        
        while True:
            samples, read = src()
            is_beat = tempo(samples)
            if is_beat:
                tempo_values.append(tempo.get_bpm())
            if read < self.hop_size:
                break
        
        # Return median BPM if we have values, otherwise default
        if tempo_values:
            return float(np.median(tempo_values))
        else:
            return 120.0
    
    def _detect_key_aubio(self, audio_file: str) -> str:
        """Detect key using aubio."""
        # Load audio file
        src = aubio.source(audio_file, self.sample_rate, self.hop_size)
        
        # Create pitch detector
        pitch = aubio.pitch("default", self.hop_size, self.hop_size, self.sample_rate)
        pitch.set_unit("midi")
        pitch.set_silence(-40)
        
        # Process audio and collect pitch values
        pitches = []
        while True:
            samples, read = src()
            pitch_value = pitch(samples)[0]
            if pitch_value > 0:  # Valid pitch
                pitches.append(pitch_value)
            if read < self.hop_size:
                break
        
        if not pitches:
            return "C"
        
        # Convert MIDI pitches to key
        return self._midi_to_key(np.median(pitches))
    
    def _midi_to_key(self, midi_note: float) -> str:
        """Convert MIDI note number to key name."""
        key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        note_idx = int(round(midi_note)) % 12
        return key_names[note_idx]


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
