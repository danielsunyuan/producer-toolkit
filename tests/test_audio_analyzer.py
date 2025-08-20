"""
Tests for the audio analyzer module with aubio integration.
"""

import os
import unittest
import tempfile
import numpy as np
import soundfile as sf
from unittest.mock import patch, MagicMock

from producer_toolkit.analyzer.audio_analyzer import (
    AudioAnalyzer, 
    analyze_audio, 
    generate_filename_with_features
)


class TestAudioAnalyzer(unittest.TestCase):
    """Test cases for the AudioAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = AudioAnalyzer()
        
        # Create a temporary test audio file
        self.temp_dir = tempfile.mkdtemp()
        self.test_audio_path = os.path.join(self.temp_dir, "test_audio.wav")
        
        # Generate a simple sine wave for testing (440Hz for 1 second at 44.1kHz)
        sample_rate = 44100
        duration = 1.0
        frequency = 440.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = 0.5 * np.sin(2 * np.pi * frequency * t)
        
        # Save as WAV file
        sf.write(self.test_audio_path, audio_data, sample_rate)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_analyzer_initialization(self):
        """Test AudioAnalyzer initialization."""
        analyzer = AudioAnalyzer(sample_rate=48000, hop_size=256)
        self.assertEqual(analyzer.sample_rate, 48000)
        self.assertEqual(analyzer.hop_size, 256)
        self.assertEqual(analyzer.win_size, 1024)
    
    def test_detect_bpm_with_valid_audio(self):
        """Test BPM detection with valid audio file."""
        bpm = self.analyzer.detect_bpm(self.test_audio_path)
        self.assertIsInstance(bpm, float)
        self.assertGreater(bpm, 0)
        self.assertLess(bpm, 300)  # Reasonable BPM range
    
    def test_detect_key_with_valid_audio(self):
        """Test key detection with valid audio file."""
        key = self.analyzer.detect_key(self.test_audio_path)
        self.assertIsInstance(key, str)
        self.assertIn(key, ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B',
                           'Am', 'C#m', 'D#m', 'Dm', 'Em', 'F#m', 'Fm', 'Gm', 'G#m', 'Bbm', 
                           'Bm', 'Cm'])
    
    def test_analyze_combines_bpm_and_key(self):
        """Test that analyze method returns both BPM and key."""
        bpm, key = self.analyzer.analyze(self.test_audio_path)
        self.assertIsInstance(bpm, float)
        self.assertIsInstance(key, str)
        self.assertGreater(bpm, 0)
        self.assertTrue(len(key) > 0)
    
    def test_detect_bpm_with_nonexistent_file(self):
        """Test BPM detection with non-existent file."""
        fake_path = "/nonexistent/file.wav"
        bpm = self.analyzer.detect_bpm(fake_path)
        self.assertEqual(bpm, 120.0)  # Default fallback
    
    def test_detect_key_with_nonexistent_file(self):
        """Test key detection with non-existent file."""
        fake_path = "/nonexistent/file.wav"
        key = self.analyzer.detect_key(fake_path)
        self.assertEqual(key, "C")  # Default fallback
    
    @patch('producer_toolkit.analyzer.audio_analyzer.sf.read')
    def test_detect_bpm_with_corrupted_file(self, mock_read):
        """Test BPM detection with corrupted audio file."""
        mock_read.side_effect = Exception("Corrupted file")
        bpm = self.analyzer.detect_bpm(self.test_audio_path)
        self.assertEqual(bpm, 120.0)  # Default fallback
    
    @patch('producer_toolkit.analyzer.audio_analyzer.sf.read')
    def test_detect_key_with_corrupted_file(self, mock_read):
        """Test key detection with corrupted audio file."""
        mock_read.side_effect = Exception("Corrupted file")
        key = self.analyzer.detect_key(self.test_audio_path)
        self.assertEqual(key, "C")  # Default fallback


class TestAnalyzeAudioFunction(unittest.TestCase):
    """Test cases for the analyze_audio convenience function."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary test audio file
        self.temp_dir = tempfile.mkdtemp()
        self.test_audio_path = os.path.join(self.temp_dir, "test_audio.wav")
        
        # Generate a simple sine wave for testing
        sample_rate = 44100
        duration = 1.0
        frequency = 440.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = 0.5 * np.sin(2 * np.pi * frequency * t)
        
        sf.write(self.test_audio_path, audio_data, sample_rate)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_analyze_audio_with_valid_file(self):
        """Test analyze_audio function with valid file."""
        bpm, key = analyze_audio(self.test_audio_path)
        self.assertIsInstance(bpm, float)
        self.assertIsInstance(key, str)
        self.assertGreater(bpm, 0)
        self.assertTrue(len(key) > 0)
    
    def test_analyze_audio_with_nonexistent_file(self):
        """Test analyze_audio function with non-existent file."""
        with self.assertRaises(FileNotFoundError):
            analyze_audio("/nonexistent/file.wav")
    
    def test_analyze_audio_with_custom_sample_rate(self):
        """Test analyze_audio function with custom sample rate."""
        bpm, key = analyze_audio(self.test_audio_path, sample_rate=48000)
        self.assertIsInstance(bpm, float)
        self.assertIsInstance(key, str)


class TestGenerateFilenameWithFeatures(unittest.TestCase):
    """Test cases for the filename generation function."""
    
    def test_generate_filename_basic(self):
        """Test basic filename generation."""
        result = generate_filename_with_features("test_song.wav", 120.0, "C")
        self.assertEqual(result, "test_song_120bpm_C.wav")
    
    def test_generate_filename_with_decimal_bpm(self):
        """Test filename generation with decimal BPM."""
        result = generate_filename_with_features("test_song.wav", 125.5, "Am")
        self.assertEqual(result, "test_song_125.5bpm_Am.wav")
    
    def test_generate_filename_with_sharp_key(self):
        """Test filename generation with sharp key."""
        result = generate_filename_with_features("test_song.mp3", 140.0, "F#")
        self.assertEqual(result, "test_song_140bpm_F#.mp3")
    
    def test_generate_filename_no_extension(self):
        """Test filename generation without extension."""
        result = generate_filename_with_features("test_song", 110.0, "Dm")
        self.assertEqual(result, "test_song_110bpm_Dm")
    
    def test_generate_filename_removes_existing_features(self):
        """Test that existing BPM/key info is removed."""
        result = generate_filename_with_features("test_song_130bpm_G.wav", 120.0, "C")
        self.assertEqual(result, "test_song_120bpm_C.wav")
    
    def test_generate_filename_cleans_underscores(self):
        """Test that trailing underscores are cleaned up."""
        result = generate_filename_with_features("test_song_", 120.0, "C")
        self.assertEqual(result, "test_song_120bpm_C")
    
    def test_generate_filename_with_integer_bpm(self):
        """Test that integer BPM values don't show decimal."""
        result = generate_filename_with_features("test.wav", 120.0, "C")
        self.assertEqual(result, "test_120bpm_C.wav")
        
        result = generate_filename_with_features("test.wav", 120.5, "C")
        self.assertEqual(result, "test_120.5bpm_C.wav")


class TestAudioAnalyzerIntegration(unittest.TestCase):
    """Integration tests for the audio analyzer module."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create different test audio files for integration testing
        sample_rate = 44100
        duration = 2.0  # Longer duration for better analysis
        
        # Test file 1: 440Hz sine wave
        self.test_audio_1 = os.path.join(self.temp_dir, "sine_440.wav")
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data_1 = 0.5 * np.sin(2 * np.pi * 440 * t)
        sf.write(self.test_audio_1, audio_data_1, sample_rate)
        
        # Test file 2: Different frequency
        self.test_audio_2 = os.path.join(self.temp_dir, "sine_880.wav")
        audio_data_2 = 0.5 * np.sin(2 * np.pi * 880 * t)
        sf.write(self.test_audio_2, audio_data_2, sample_rate)
        
        # Test file 3: Stereo file
        self.test_audio_stereo = os.path.join(self.temp_dir, "stereo.wav")
        stereo_data = np.column_stack([audio_data_1, audio_data_2])
        sf.write(self.test_audio_stereo, stereo_data, sample_rate)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_analyzer_handles_stereo_files(self):
        """Test that analyzer can handle stereo audio files."""
        analyzer = AudioAnalyzer()
        bpm, key = analyzer.analyze(self.test_audio_stereo)
        self.assertIsInstance(bpm, float)
        self.assertIsInstance(key, str)
        self.assertGreater(bpm, 0)
    
    def test_multiple_file_analysis(self):
        """Test analyzing multiple different files."""
        analyzer = AudioAnalyzer()
        
        results = []
        for test_file in [self.test_audio_1, self.test_audio_2]:
            bpm, key = analyzer.analyze(test_file)
            results.append((bpm, key))
        
        # Each analysis should return valid results
        for bpm, key in results:
            self.assertIsInstance(bpm, float)
            self.assertIsInstance(key, str)
            self.assertGreater(bpm, 0)
            self.assertTrue(len(key) > 0)


if __name__ == '__main__':
    unittest.main()
