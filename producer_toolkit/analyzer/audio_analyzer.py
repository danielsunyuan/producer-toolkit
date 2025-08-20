"""
Audio analysis module using aubio for BPM and key detection.

This module provides functionality to analyze audio files and extract
musical features such as tempo (BPM) and key information.
"""

import os
import numpy as np
import aubio
import soundfile as sf
from typing import Tuple, Optional


class AudioAnalyzer:
    """Audio analyzer class for extracting musical features from audio files."""
    
    def __init__(self, sample_rate: int = 44100, hop_size: int = 512):
        """
        Initialize the AudioAnalyzer.
        
        Args:
            sample_rate: Sample rate for audio processing (default: 44100)
            hop_size: Hop size for analysis window (default: 512)
        """
        self.sample_rate = sample_rate
        self.hop_size = hop_size
        self.win_size = 1024  # Window size for analysis
        
    def detect_bpm(self, audio_file: str) -> float:
        """
        Detect the BPM (beats per minute) of an audio file.
        
        Args:
            audio_file: Path to the audio file
            
        Returns:
            BPM as a float value
        """
        try:
            # Load audio file
            audio_data, original_sr = sf.read(audio_file)
            
            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            
            # Resample if necessary
            if original_sr != self.sample_rate:
                import librosa
                audio_data = librosa.resample(audio_data, orig_sr=original_sr, target_sr=self.sample_rate)
            
            # Convert to float32 for aubio
            audio_data = audio_data.astype(np.float32)
            
            # Create aubio tempo detection object
            tempo_detector = aubio.tempo("default", self.win_size, self.hop_size, self.sample_rate)
            
            # Process audio in chunks
            beats = []
            for i in range(0, len(audio_data) - self.hop_size, self.hop_size):
                chunk = audio_data[i:i + self.hop_size]
                if len(chunk) < self.hop_size:
                    # Pad with zeros if chunk is too small
                    chunk = np.pad(chunk, (0, self.hop_size - len(chunk)))
                
                is_beat = tempo_detector(chunk)
                if is_beat:
                    beat_time = tempo_detector.get_last_s()
                    beats.append(beat_time)
            
            # Calculate BPM from detected beats
            if len(beats) >= 2:
                # Calculate intervals between beats
                intervals = np.diff(beats)
                # Remove outliers (intervals that are too different from the median)
                median_interval = np.median(intervals)
                valid_intervals = intervals[np.abs(intervals - median_interval) < median_interval * 0.5]
                
                if len(valid_intervals) > 0:
                    avg_interval = np.mean(valid_intervals)
                    bpm = 60.0 / avg_interval
                    return round(bpm, 1)
            
            # Fallback: get BPM directly from tempo detector
            bpm = tempo_detector.get_bpm()
            return round(bpm, 1) if bpm > 0 else 120.0
            
        except Exception as e:
            print(f"Warning: BPM detection failed ({str(e)}), using default 120.0")
            return 120.0
    
    def detect_key(self, audio_file: str) -> str:
        """
        Detect the musical key of an audio file.
        
        Args:
            audio_file: Path to the audio file
            
        Returns:
            Musical key as a string (e.g., "C", "Am", "F#")
        """
        try:
            # Load audio file
            audio_data, original_sr = sf.read(audio_file)
            
            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            
            # Resample if necessary
            if original_sr != self.sample_rate:
                import librosa
                audio_data = librosa.resample(audio_data, orig_sr=original_sr, target_sr=self.sample_rate)
            
            # Convert to float32 for aubio
            audio_data = audio_data.astype(np.float32)
            
            # Create pitch detection object
            pitch_detector = aubio.pitch("yin", self.win_size, self.hop_size, self.sample_rate)
            pitch_detector.set_unit("Hz")
            pitch_detector.set_silence(-40)
            
            # Detect pitches throughout the audio
            pitches = []
            confidences = []
            
            for i in range(0, len(audio_data) - self.hop_size, self.hop_size):
                chunk = audio_data[i:i + self.hop_size]
                if len(chunk) < self.hop_size:
                    chunk = np.pad(chunk, (0, self.hop_size - len(chunk)))
                
                pitch = pitch_detector(chunk)
                confidence = pitch_detector.get_confidence()
                
                if confidence > 0.5 and pitch > 0:  # Only consider confident pitch detections
                    pitches.append(pitch)
                    confidences.append(confidence)
            
            if not pitches:
                return "C"  # Default key if no pitches detected
            
            # Convert frequencies to MIDI notes
            def freq_to_midi(freq):
                return 69 + 12 * np.log2(freq / 440.0)
            
            def midi_to_note(midi):
                notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
                return notes[int(midi) % 12]
            
            # Get the most common pitch class
            midi_notes = [freq_to_midi(p) for p in pitches]
            note_classes = [midi_to_note(m) for m in midi_notes]
            
            # Count frequency of each note class
            from collections import Counter
            note_counts = Counter(note_classes)
            
            if note_counts:
                most_common_note = note_counts.most_common(1)[0][0]
                
                # Simple major/minor detection based on interval analysis
                # This is a simplified approach - in reality, key detection is much more complex
                major_keys = ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'F', 'Bb', 'Eb', 'Ab', 'Db']
                minor_keys = ['Am', 'Em', 'Bm', 'F#m', 'C#m', 'G#m', 'D#m', 'Dm', 'Gm', 'Cm', 'Fm', 'Bbm']
                
                # For simplicity, assume major key based on most common note
                # A more sophisticated algorithm would analyze the harmonic content
                if most_common_note in ['C', 'G', 'D', 'A', 'E', 'B', 'F#', 'F']:
                    return most_common_note
                else:
                    # Return as minor key
                    minor_map = {'C#': 'C#m', 'D#': 'D#m', 'G#': 'G#m', 'A#': 'Bbm'}
                    return minor_map.get(most_common_note, f"{most_common_note}m")
            
            return "C"  # Default fallback
            
        except Exception as e:
            print(f"Warning: Key detection failed ({str(e)}), using default 'C'")
            return "C"
    
    def analyze(self, audio_file: str) -> Tuple[float, str]:
        """
        Analyze an audio file to extract both BPM and key.
        
        Args:
            audio_file: Path to the audio file
            
        Returns:
            Tuple of (bpm, key)
        """
        bpm = self.detect_bpm(audio_file)
        key = self.detect_key(audio_file)
        return bpm, key


def analyze_audio(audio_file: str, sample_rate: int = 44100) -> Tuple[float, str]:
    """
    Convenience function to analyze an audio file and return BPM and key.
    
    Args:
        audio_file: Path to the audio file
        sample_rate: Sample rate for analysis (default: 44100)
        
    Returns:
        Tuple of (bpm, key)
    """
    if not os.path.exists(audio_file):
        raise FileNotFoundError(f"Audio file not found: {audio_file}")
    
    analyzer = AudioAnalyzer(sample_rate=sample_rate)
    return analyzer.analyze(audio_file)


def generate_filename_with_features(base_filename: str, bpm: float, key: str) -> str:
    """
    Generate a filename that includes BPM and key information.
    
    Args:
        base_filename: Original filename (with or without extension)
        bpm: BPM value
        key: Musical key
        
    Returns:
        Enhanced filename with BPM and key information
    """
    # Split filename and extension
    name, ext = os.path.splitext(base_filename)
    
    # Clean up the name (remove any existing BPM/key info to avoid duplication)
    import re
    name = re.sub(r'_\d+(\.\d+)?bpm.*', '', name)  # Remove existing BPM info
    name = re.sub(r'_[A-G][#b]?m?_', '_', name)    # Remove existing key info
    name = name.rstrip('_')  # Remove trailing underscores
    
    # Format BPM (remove decimal if it's .0)
    bpm_str = f"{int(bpm)}" if bpm == int(bpm) else f"{bpm:.1f}"
    
    # Create new filename with features
    enhanced_name = f"{name}_{bpm_str}bpm_{key}{ext}"
    
    return enhanced_name
