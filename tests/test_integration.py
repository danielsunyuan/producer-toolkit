"""
Integration tests for Producer Toolkit.

Tests the full pipeline: YouTube download → stem extraction (4-stem and 2-stem).
"""

import os
import sys
import unittest
import tempfile
import shutil
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from producer_toolkit.downloader.download import download_audio
from producer_toolkit.processor.demucs_processor import extract_stems
from producer_toolkit.analyzer.audio_analyzer import analyze_audio


class TestYouTubeDownload(unittest.TestCase):
    """Test YouTube audio download functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_url = "https://www.youtube.com/watch?v=q6EoRBvdVPQ&pp=ygUDeWVl"
        self.temp_dir = tempfile.mkdtemp()
        self.downloaded_file = None
    
    def tearDown(self):
        """Clean up test fixtures."""
        if self.downloaded_file and os.path.exists(self.downloaded_file):
            os.remove(self.downloaded_file)
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @unittest.skipIf(
        os.getenv("SKIP_YOUTUBE_TESTS") == "true",
        "Skipping YouTube download test (set SKIP_YOUTUBE_TESTS=false to enable)"
    )
    def test_download_youtube_audio(self):
        """Test downloading audio from YouTube."""
        print("\n📥 Testing YouTube download...")
        
        # Download audio (no BPM/key analysis for audio-only)
        self.downloaded_file = download_audio(self.test_url, self.temp_dir, analyze_features=False)
        
        # Verify file was downloaded
        self.assertIsNotNone(self.downloaded_file, "Download should return a file path")
        self.assertTrue(os.path.exists(self.downloaded_file), f"Downloaded file should exist: {self.downloaded_file}")
        self.assertGreater(os.path.getsize(self.downloaded_file), 0, "Downloaded file should not be empty")
        
        # Verify it's a WAV file
        self.assertTrue(self.downloaded_file.endswith('.wav'), "Downloaded file should be WAV format")
        
        print(f"✅ Downloaded: {os.path.basename(self.downloaded_file)}")
        print(f"   Size: {os.path.getsize(self.downloaded_file) / 1024 / 1024:.2f} MB")


class TestStemExtraction(unittest.TestCase):
    """Test stem extraction functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Use the Yee.wav file from test resources
        project_root = Path(__file__).resolve().parent.parent
        self.test_file = project_root / "tests" / "resources" / "Yee.wav"
        
        # Fallback to sample.wav if Yee.wav doesn't exist
        if not self.test_file.exists():
            self.test_file = project_root / "tests" / "resources" / "sample.wav"
        
        if not self.test_file.exists():
            self.skipTest("No test audio file available (Yee.wav or tests/resources/sample.wav)")
        
        self.output_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
    
    def test_4_stem_extraction(self):
        """Test 4-stem extraction (vocals, drums, bass, other)."""
        print(f"\n🔧 Testing 4-stem extraction with: {self.test_file.name}")
        
        extract_stems(
            str(self.test_file),
            self.output_dir,
            stem_number=4,
            analyze_features=True  # Test BPM/key analysis during stem extraction
        )
        
        # Verify output directory was created
        self.assertTrue(os.path.exists(self.output_dir), "Output directory should exist")
        
        # Verify all 4 stems were created (may have BPM/key in filename)
        expected_stem_names = ["vocals", "drums", "bass", "other"]
        found_stems = []
        for file in os.listdir(self.output_dir):
            if file.endswith('.wav'):
                for stem_name in expected_stem_names:
                    if file.startswith(stem_name):
                        found_stems.append(stem_name)
                        stem_path = os.path.join(self.output_dir, file)
                        self.assertGreater(os.path.getsize(stem_path), 0, f"Stem {file} should not be empty")
                        print(f"   ✅ {file} ({os.path.getsize(stem_path) / 1024:.2f} KB)")
                        break
        
        # Verify we found all expected stems
        for stem_name in expected_stem_names:
            self.assertIn(stem_name, found_stems, f"Stem containing '{stem_name}' should exist")
    
    def test_2_stem_extraction(self):
        """Test 2-stem extraction (vocals, accompaniment)."""
        print(f"\n🔧 Testing 2-stem extraction with: {self.test_file.name}")
        
        extract_stems(
            str(self.test_file),
            self.output_dir,
            stem_number=2,
            analyze_features=True  # Test BPM/key analysis during stem extraction
        )
        
        # Verify output directory was created
        self.assertTrue(os.path.exists(self.output_dir), "Output directory should exist")
        
        # Verify both stems were created (may have BPM/key in filename)
        expected_stem_names = ["vocals", "no_vocals"]
        found_stems = []
        for file in os.listdir(self.output_dir):
            if file.endswith('.wav'):
                for stem_name in expected_stem_names:
                    if file.startswith(stem_name):
                        found_stems.append(stem_name)
                        stem_path = os.path.join(self.output_dir, file)
                        self.assertGreater(os.path.getsize(stem_path), 0, f"Stem {file} should not be empty")
                        print(f"   ✅ {file} ({os.path.getsize(stem_path) / 1024:.2f} KB)")
                        break
        
        # Verify we found all expected stems
        for stem_name in expected_stem_names:
            self.assertIn(stem_name, found_stems, f"Stem containing '{stem_name}' should exist")


class TestFullPipeline(unittest.TestCase):
    """Test the full pipeline: download → analyze → extract stems."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_url = "https://www.youtube.com/watch?v=q6EoRBvdVPQ&pp=ygUDeWVl"
        self.temp_dir = tempfile.mkdtemp()
        self.downloaded_file = None
        self.stems_dir = os.path.join(self.temp_dir, "stems")
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    @unittest.skipIf(
        os.getenv("SKIP_YOUTUBE_TESTS") == "true",
        "Skipping full pipeline test (set SKIP_YOUTUBE_TESTS=false to enable)"
    )
    def test_full_pipeline_4_stem(self):
        """Test full pipeline: download → extract 4 stems with analysis."""
        print("\n🎵 Testing full pipeline (download → 4-stem extraction)...")
        
        # Step 1: Download audio
        print("   Step 1: Downloading audio...")
        self.downloaded_file = download_audio(self.test_url, self.temp_dir, analyze_features=False)
        self.assertIsNotNone(self.downloaded_file)
        self.assertTrue(os.path.exists(self.downloaded_file))
        print(f"   ✅ Downloaded: {os.path.basename(self.downloaded_file)}")
        
        # Step 2: Extract 4 stems with BPM/key analysis
        print("   Step 2: Extracting 4 stems with analysis...")
        extract_stems(
            self.downloaded_file,
            self.stems_dir,
            stem_number=4,
            analyze_features=True
        )
        
        # Verify stems were created (may have BPM/key in filename)
        expected_stem_names = ["vocals", "drums", "bass", "other"]
        found_stems = []
        for file in os.listdir(self.stems_dir):
            if file.endswith('.wav'):
                for stem_name in expected_stem_names:
                    if file.startswith(stem_name):
                        found_stems.append(stem_name)
                        break
        
        # Verify we found all expected stems
        for stem_name in expected_stem_names:
            self.assertIn(stem_name, found_stems, f"Stem containing '{stem_name}' should exist")
        
        print(f"   ✅ 4-stem extraction complete!")
        print(f"   📁 Output: {self.stems_dir}")
    
    @unittest.skipIf(
        os.getenv("SKIP_YOUTUBE_TESTS") == "true",
        "Skipping full pipeline test (set SKIP_YOUTUBE_TESTS=false to enable)"
    )
    def test_full_pipeline_2_stem(self):
        """Test full pipeline: download → extract 2 stems with analysis."""
        print("\n🎵 Testing full pipeline (download → 2-stem extraction)...")
        
        # Step 1: Download audio
        print("   Step 1: Downloading audio...")
        self.downloaded_file = download_audio(self.test_url, self.temp_dir, analyze_features=False)
        self.assertIsNotNone(self.downloaded_file)
        self.assertTrue(os.path.exists(self.downloaded_file))
        print(f"   ✅ Downloaded: {os.path.basename(self.downloaded_file)}")
        
        # Step 2: Extract 2 stems with BPM/key analysis
        print("   Step 2: Extracting 2 stems with analysis...")
        extract_stems(
            self.downloaded_file,
            self.stems_dir,
            stem_number=2,
            analyze_features=True
        )
        
        # Verify stems were created (may have BPM/key in filename)
        expected_stem_names = ["vocals", "no_vocals"]
        found_stems = []
        for file in os.listdir(self.stems_dir):
            if file.endswith('.wav'):
                for stem_name in expected_stem_names:
                    if file.startswith(stem_name):
                        found_stems.append(stem_name)
                        break
        
        # Verify we found all expected stems
        for stem_name in expected_stem_names:
            self.assertIn(stem_name, found_stems, f"Stem containing '{stem_name}' should exist")
        
        print(f"   ✅ 2-stem extraction complete!")
        print(f"   📁 Output: {self.stems_dir}")


class TestLocalAudioFile(unittest.TestCase):
    """Test stem extraction using local Yee.wav file."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Look for Yee.wav in test resources
        project_root = Path(__file__).resolve().parent.parent
        self.audio_file = project_root / "tests" / "resources" / "Yee.wav"
        
        if not self.audio_file.exists():
            self.skipTest("Yee.wav not found in tests/resources/")
        
        self.output_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
    
    def test_local_file_4_stem_extraction(self):
        """Test 4-stem extraction using local Yee.wav file."""
        print(f"\n🔧 Testing 4-stem extraction with local file: {self.audio_file.name}")
        print(f"   File size: {self.audio_file.stat().st_size / 1024 / 1024:.2f} MB")
        
        extract_stems(
            str(self.audio_file),
            self.output_dir,
            stem_number=4,
            analyze_features=True
        )
        
        # Verify all 4 stems were created (may have BPM/key in filename)
        expected_stem_names = ["vocals", "drums", "bass", "other"]
        found_stems = []
        for file in os.listdir(self.output_dir):
            if file.endswith('.wav'):
                for stem_name in expected_stem_names:
                    if file.startswith(stem_name):
                        found_stems.append(stem_name)
                        stem_path = os.path.join(self.output_dir, file)
                        file_size = os.path.getsize(stem_path) / 1024 / 1024
                        print(f"   ✅ {file} ({file_size:.2f} MB)")
                        break
        
        # Verify we found all expected stems
        for stem_name in expected_stem_names:
            self.assertIn(stem_name, found_stems, f"Stem containing '{stem_name}' should exist")
    
    def test_local_file_2_stem_extraction(self):
        """Test 2-stem extraction using local Yee.wav file."""
        print(f"\n🔧 Testing 2-stem extraction with local file: {self.audio_file.name}")
        print(f"   File size: {self.audio_file.stat().st_size / 1024 / 1024:.2f} MB")
        
        extract_stems(
            str(self.audio_file),
            self.output_dir,
            stem_number=2,
            analyze_features=True
        )
        
        # Verify both stems were created (may have BPM/key in filename)
        expected_stem_names = ["vocals", "no_vocals"]
        found_stems = []
        for file in os.listdir(self.output_dir):
            if file.endswith('.wav'):
                for stem_name in expected_stem_names:
                    if file.startswith(stem_name):
                        found_stems.append(stem_name)
                        stem_path = os.path.join(self.output_dir, file)
                        file_size = os.path.getsize(stem_path) / 1024 / 1024
                        print(f"   ✅ {file} ({file_size:.2f} MB)")
                        break
        
        # Verify we found all expected stems
        for stem_name in expected_stem_names:
            self.assertIn(stem_name, found_stems, f"Stem containing '{stem_name}' should exist")
    
    def test_local_file_audio_analysis(self):
        """Test BPM and key detection on local Yee.wav file."""
        print(f"\n🎵 Testing audio analysis on: {self.audio_file.name}")
        
        bpm, key = analyze_audio(str(self.audio_file))
        
        # Verify results
        self.assertIsInstance(bpm, float)
        self.assertGreater(bpm, 0)
        self.assertLess(bpm, 300)  # Reasonable BPM range
        
        self.assertIsInstance(key, str)
        self.assertTrue(len(key) > 0)
        
        print(f"   ✅ Detected: {bpm:.2f} BPM, Key: {key}")


if __name__ == "__main__":
    # Allow skipping YouTube tests via environment variable
    print("=" * 60)
    print("Producer Toolkit Integration Tests")
    print("=" * 60)
    print("\nNote: YouTube tests can be skipped by setting SKIP_YOUTUBE_TESTS=true")
    print("Example: SKIP_YOUTUBE_TESTS=true python -m unittest tests.test_integration\n")
    
    unittest.main(verbosity=2)

