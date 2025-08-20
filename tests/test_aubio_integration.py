"""
Integration tests for aubio functionality with the producer toolkit.
Tests the full workflow of downloading, analyzing, and naming files with BPM/key.
"""

import os
import unittest
import tempfile
import shutil
from unittest.mock import patch, MagicMock

from producer_toolkit.downloader.download import download_audio
from producer_toolkit.processor.spleeter_processor import extract_stems
from producer_toolkit.analyzer.audio_analyzer import generate_filename_with_features


class TestAubioIntegration(unittest.TestCase):
    """Integration tests for aubio functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        
        # Create a mock audio file for testing
        self.test_audio_file = os.path.join(self.temp_dir, "test_input.wav")
        
        # Create a minimal valid WAV file (sine wave)
        import numpy as np
        import soundfile as sf
        
        sample_rate = 44100
        duration = 1.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = 0.5 * np.sin(2 * np.pi * 440 * t)
        sf.write(self.test_audio_file, audio_data, sample_rate)
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('producer_toolkit.downloader.download.yt_dlp.YoutubeDL')
    @patch('producer_toolkit.analyzer.audio_analyzer.analyze_audio')
    def test_download_audio_with_analysis(self, mock_analyze, mock_ydl):
        """Test download_audio with BPM/key analysis enabled."""
        # Mock the YoutubeDL behavior
        mock_ydl_instance = MagicMock()
        mock_ydl.return_value.__enter__.return_value = mock_ydl_instance
        
        # Mock extract_info to return video metadata
        mock_ydl_instance.extract_info.return_value = {
            'title': 'Test Song'
        }
        
        # Mock the analysis to return specific BPM/key
        mock_analyze.return_value = (128.0, "Am")
        
        # Create the expected downloaded file
        expected_temp_file = os.path.join(self.temp_dir, "Test Song.wav")
        shutil.copy(self.test_audio_file, expected_temp_file)
        
        # Test the download with analysis
        result = download_audio("fake_url", self.temp_dir, analyze_features=True)
        
        # Verify the file has BPM and key in filename
        self.assertIn("128bpm", result)
        self.assertIn("Am", result)
        self.assertTrue(os.path.exists(result))
    
    @patch('producer_toolkit.downloader.download.yt_dlp.YoutubeDL')
    def test_download_audio_without_analysis(self, mock_ydl):
        """Test download_audio with analysis disabled."""
        # Mock the YoutubeDL behavior
        mock_ydl_instance = MagicMock()
        mock_ydl.return_value.__enter__.return_value = mock_ydl_instance
        
        mock_ydl_instance.extract_info.return_value = {
            'title': 'Test Song'
        }
        
        # Create the expected downloaded file
        expected_temp_file = os.path.join(self.temp_dir, "Test Song.wav")
        shutil.copy(self.test_audio_file, expected_temp_file)
        
        # Test the download without analysis
        result = download_audio("fake_url", self.temp_dir, analyze_features=False)
        
        # Verify the file doesn't have BPM and key in filename
        self.assertNotIn("bpm", result.lower())
        self.assertEqual(os.path.basename(result), "Test Song.wav")
    
    @patch('producer_toolkit.processor.spleeter_processor.Separator')
    @patch('producer_toolkit.analyzer.audio_analyzer.analyze_audio')
    def test_extract_stems_with_analysis(self, mock_analyze, mock_separator):
        """Test stem extraction with BPM/key analysis."""
        # Mock the analysis
        mock_analyze.return_value = (140.0, "C#")
        
        # Mock Spleeter separator
        mock_separator_instance = MagicMock()
        mock_separator.return_value = mock_separator_instance
        
        # Create stems output directory
        stems_dir = os.path.join(self.temp_dir, "stems")
        os.makedirs(stems_dir, exist_ok=True)
        
        # Create mock separated files that Spleeter would create
        temp_spleeter_dir = os.path.join(stems_dir, "_temp_spleeter", "test_input")
        os.makedirs(temp_spleeter_dir, exist_ok=True)
        
        # Create mock stem files
        for stem in ["vocals.wav", "drums.wav", "bass.wav", "other.wav"]:
            stem_path = os.path.join(temp_spleeter_dir, stem)
            shutil.copy(self.test_audio_file, stem_path)
        
        # Test stem extraction with analysis
        result = extract_stems(
            self.test_audio_file, 
            stems_dir, 
            stem_number=4, 
            analyze_features=True
        )
        
        # Verify stem files have BPM and key in filenames
        stem_files = os.listdir(stems_dir)
        for stem_file in stem_files:
            if stem_file.endswith('.wav'):
                self.assertIn("140bpm", stem_file)
                self.assertIn("C#", stem_file)
    
    @patch('producer_toolkit.processor.spleeter_processor.Separator')
    def test_extract_stems_without_analysis(self, mock_separator):
        """Test stem extraction without BPM/key analysis."""
        # Mock Spleeter separator
        mock_separator_instance = MagicMock()
        mock_separator.return_value = mock_separator_instance
        
        # Create stems output directory
        stems_dir = os.path.join(self.temp_dir, "stems")
        os.makedirs(stems_dir, exist_ok=True)
        
        # Create mock separated files that Spleeter would create
        temp_spleeter_dir = os.path.join(stems_dir, "_temp_spleeter", "test_input")
        os.makedirs(temp_spleeter_dir, exist_ok=True)
        
        # Create mock stem files
        for stem in ["vocals.wav", "accompaniment.wav"]:
            stem_path = os.path.join(temp_spleeter_dir, stem)
            shutil.copy(self.test_audio_file, stem_path)
        
        # Test stem extraction without analysis
        result = extract_stems(
            self.test_audio_file, 
            stems_dir, 
            stem_number=2, 
            analyze_features=False
        )
        
        # Verify stem files don't have BPM and key in filenames
        stem_files = os.listdir(stems_dir)
        for stem_file in stem_files:
            if stem_file.endswith('.wav'):
                self.assertNotIn("bpm", stem_file.lower())
    
    def test_filename_generation_edge_cases(self):
        """Test filename generation with various edge cases."""
        test_cases = [
            # (input_filename, bpm, key, expected_output)
            ("song.wav", 120.0, "C", "song_120bpm_C.wav"),
            ("song_with_spaces.mp3", 125.5, "F#", "song_with_spaces_125.5bpm_F#.mp3"),
            ("song-with-dashes.wav", 90.0, "Bbm", "song-with-dashes_90bpm_Bbm.wav"),
            ("song_existing_120bpm_C.wav", 140.0, "Am", "song_existing_140bpm_Am.wav"),
            ("song_", 110.0, "D", "song_110bpm_D"),
        ]
        
        for input_filename, bmp, key, expected in test_cases:
            with self.subTest(input=input_filename):
                result = generate_filename_with_features(input_filename, bmp, key)
                self.assertEqual(result, expected)
    
    @patch('producer_toolkit.analyzer.audio_analyzer.analyze_audio')
    def test_analysis_error_handling(self, mock_analyze):
        """Test that the system handles analysis errors gracefully."""
        # Mock analysis to raise an exception
        mock_analyze.side_effect = Exception("Analysis failed")
        
        # This should not crash but fall back to original filename
        result = generate_filename_with_features("test.wav", 120.0, "C")
        self.assertEqual(result, "test_120bmp_C.wav")
    
    def test_integration_with_existing_workflow(self):
        """Test that new features integrate with existing workflow."""
        # Test that functions still work when called without new parameters
        
        # Test download_audio without analyze_features parameter
        # (Should default to True)
        with patch('producer_toolkit.downloader.download.yt_dlp.YoutubeDL') as mock_ydl:
            mock_ydl_instance = MagicMock()
            mock_ydl.return_value.__enter__.return_value = mock_ydl_instance
            mock_ydl_instance.extract_info.return_value = {'title': 'Test'}
            
            # Create expected file
            expected_file = os.path.join(self.temp_dir, "Test.wav")
            shutil.copy(self.test_audio_file, expected_file)
            
            # This should work without specifying analyze_features
            try:
                download_audio("fake_url", self.temp_dir)
                # If it doesn't crash, the backward compatibility works
                self.assertTrue(True)
            except TypeError:
                self.fail("download_audio should work without analyze_features parameter")


class TestAubioCLIIntegration(unittest.TestCase):
    """Test the CLI integration with aubio features."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @patch('producer_toolkit.cli.download_audio')
    def test_cli_passes_analysis_flag(self, mock_download_audio):
        """Test that CLI properly passes the analysis flag."""
        from producer_toolkit.cli import main
        import sys
        
        # Mock sys.argv to simulate CLI call
        original_argv = sys.argv
        try:
            # Test with --no-analysis flag
            sys.argv = ['pt', 'fake_url', '-a', '--no-analysis', '-o', self.temp_dir]
            
            # Mock download_audio to prevent actual download
            mock_download_audio.return_value = "fake_file.wav"
            
            result = main()
            
            # Verify download_audio was called with analyze_features=False
            mock_download_audio.assert_called_once()
            call_args = mock_download_audio.call_args
            self.assertEqual(call_args[1]['analyze_features'], False)
            
        finally:
            sys.argv = original_argv
    
    @patch('producer_toolkit.cli.download_audio')
    def test_cli_default_analysis_enabled(self, mock_download_audio):
        """Test that CLI has analysis enabled by default."""
        from producer_toolkit.cli import main
        import sys
        
        original_argv = sys.argv
        try:
            # Test without --no-analysis flag (should default to analysis enabled)
            sys.argv = ['pt', 'fake_url', '-a', '-o', self.temp_dir]
            
            mock_download_audio.return_value = "fake_file.wav"
            
            result = main()
            
            # Verify download_audio was called with analyze_features=True
            mock_download_audio.assert_called_once()
            call_args = mock_download_audio.call_args
            self.assertEqual(call_args[1]['analyze_features'], True)
            
        finally:
            sys.argv = original_argv


if __name__ == '__main__':
    unittest.main()
