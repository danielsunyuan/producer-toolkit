"""
Audio analyzer module for BPM and key detection using aubio or librosa fallback.
"""

import os
import logging
from typing import Tuple, Optional
import soundfile as sf
import numpy as np

logger = logging.getLogger(__name__)

# Try to import aubio, fallback to librosa if not available
try:
    import aubio
    # Check if aubio actually has the required functions
    if hasattr(aubio, 'source') and hasattr(aubio, 'tempo') and hasattr(aubio, 'pitch'):
        AUBIO_AVAILABLE = True
    else:
        AUBIO_AVAILABLE = False
        logger.warning("Aubio imported but missing required functions, falling back to librosa")
except ImportError:
    AUBIO_AVAILABLE = False

try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    LIBROSA_AVAILABLE = False


class AudioAnalyzer:
    """
    Audio analyzer for detecting BPM and musical key from audio files.
    
    Uses aubio for analysis when available, falls back to librosa if needed.
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
        
        if not AUBIO_AVAILABLE and not LIBROSA_AVAILABLE:
            logger.warning("Neither aubio nor librosa available. Audio analysis will use fallback values.")
    
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
            if AUBIO_AVAILABLE:
                return self._detect_bpm_aubio(audio_file)
            elif LIBROSA_AVAILABLE:
                return self._detect_bpm_librosa(audio_file)
            else:
                logger.warning("No audio analysis libraries available, using fallback BPM")
                return 120.0
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
            if AUBIO_AVAILABLE:
                return self._detect_key_aubio(audio_file)
            elif LIBROSA_AVAILABLE:
                return self._detect_key_librosa(audio_file)
            else:
                logger.warning("No audio analysis libraries available, using fallback key")
                return "C"
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
        try:
            # Load audio file
            src = aubio.source(audio_file, self.sample_rate, self.hop_size)
            
            # Create tempo detector
            tempo = aubio.tempo("default", self.hop_size, self.hop_size, self.sample_rate)
            
            # Process audio in chunks
            total_frames = 0
            tempo_values = []
            
            while True:
                samples, read = src()
                is_beat = tempo(samples)
                if is_beat:
                    tempo_values.append(tempo.get_bpm())
                total_frames += read
                if read < self.hop_size:
                    break
            
            # Return median BPM if we have values, otherwise default
            if tempo_values:
                return float(np.median(tempo_values))
            else:
                return 120.0
                
        except Exception as e:
            logger.error(f"Aubio BPM detection failed: {e}")
            return 120.0
    
    def _detect_key_aubio(self, audio_file: str) -> str:
        """Detect key using aubio."""
        try:
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
            
        except Exception as e:
            logger.error(f"Aubio key detection failed: {e}")
            return "C"
    
    def _detect_bpm_librosa(self, audio_file: str) -> float:
        """Detect BPM using librosa."""
        try:
            # Load audio file
            y, sr = librosa.load(audio_file, sr=self.sample_rate)
            
            # Use a more robust tempo detection method
            # First try the standard beat tracking
            try:
                tempo, _ = librosa.beat.beat_track(y=y, sr=sr, hop_length=self.hop_size)
                if tempo > 0:
                    return float(tempo)
            except Exception as e:
                logger.debug(f"Standard beat tracking failed: {e}")
            
            # Fallback: use onset detection and estimate tempo
            try:
                # Get onset strength
                onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=self.hop_size)
                
                # Estimate tempo from onset strength
                tempo = librosa.beat.tempo(onset_envelope=onset_env, sr=sr, hop_length=self.hop_size)
                
                if tempo > 0:
                    return float(tempo[0])
            except Exception as e:
                logger.debug(f"Onset-based tempo detection failed: {e}")
            
            # Final fallback: use spectral features
            try:
                # Extract spectral features
                spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
                
                # Simple tempo estimation based on spectral centroid variance
                # This is a rough approximation
                centroid_var = np.var(spectral_centroids)
                if centroid_var > 1000:  # High variance suggests faster tempo
                    return 140.0
                elif centroid_var > 500:
                    return 120.0
                else:
                    return 100.0
            except Exception as e:
                logger.debug(f"Spectral-based tempo estimation failed: {e}")
            
            return 120.0
            
        except Exception as e:
            logger.error(f"Librosa BPM detection failed: {e}")
            return 120.0
    
    def _detect_key_librosa(self, audio_file: str) -> str:
        """Detect key using librosa."""
        try:
            # Load audio file
            y, sr = librosa.load(audio_file, sr=self.sample_rate)
            
            # Extract chromagram with error handling
            try:
                chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=self.hop_size)
            except Exception:
                # Fallback to standard chromagram
                chroma = librosa.feature.chroma_stft(y=y, sr=sr, hop_length=self.hop_size)
            
            # Get key profile
            key_profile = np.mean(chroma, axis=1)
            
            # Simple key detection based on maximum chroma value
            key_names = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
            major_key_idx = np.argmax(key_profile)
            
            # For simplicity, assume major key
            return key_names[major_key_idx]
            
        except Exception as e:
            logger.error(f"Librosa key detection failed: {e}")
            return "C"
    
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
