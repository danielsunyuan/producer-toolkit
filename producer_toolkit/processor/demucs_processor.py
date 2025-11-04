import os
import sys
import shutil
import logging
import subprocess
from pathlib import Path
from ..analyzer.audio_analyzer import analyze_audio, generate_filename_with_features

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Reduce TensorFlow warnings if PyTorch is used
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

def extract_stems(audio_path, output_dir, stem_number=4, models_dir=None, analyze_features=True):
    """
    Splits the audio file into stems using Demucs with BPM and key analysis.
    
    Args:
        audio_path (str): Path to the input audio file (WAV format expected).
        output_dir (str): Directory where the separated stems will be saved.
        stem_number (int): Number of stems (2 or 4). Default is 4 stems.
                          Note: Demucs always produces 4 stems (vocals, drums, bass, other).
                          If 2 is specified, vocals and accompaniment (no_vocals) will be created.
        models_dir (str, optional): Directory where Demucs models should be stored.
                                   If None, defaults to Demucs default location.
        analyze_features (bool): Whether to analyze and include BPM/key in stem filenames (default: True).
    
    Returns:
        str: The output directory where stems are saved.
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Analyze audio features first if requested
    bpm, key = None, None
    if analyze_features:
        try:
            print("Analyzing audio features before stem separation...")
            bpm, key = analyze_audio(audio_path)
            print(f"Detected: {bpm} BPM, Key: {key}")
        except Exception as e:
            print(f"Warning: Audio analysis failed ({str(e)}), proceeding without features")
            analyze_features = False
    
    print(f"Processing stems with Demucs... (this may take a moment)")
    
    # Create a temporary directory for Demucs output
    temp_output = os.path.join(output_dir, "_temp_demucs")
    os.makedirs(temp_output, exist_ok=True)
    
    try:
        # Build demucs command
        # Using htdemucs model (default, latest Hybrid Transformer model)
        cmd = [
            "demucs",
            "-o", temp_output,
            "-n", "htdemucs",  # Use htdemucs model
            audio_path
        ]
        
        # Set models directory if specified
        env = os.environ.copy()
        if models_dir:
            env['DEMUCS_MODEL_DIR'] = models_dir
        
        # Run demucs
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            env=env
        )
        
        if result.returncode != 0:
            raise Exception(f"Demucs failed: {result.stderr}")
        
        # Get the filename from the audio path
        filename = os.path.splitext(os.path.basename(audio_path))[0]
        
        # Demucs creates: temp_output/htdemucs/filename/{vocals,drums,bass,other}.wav
        source_dir = os.path.join(temp_output, "htdemucs", filename)
        
        if not os.path.exists(source_dir):
            raise Exception(f"Demucs output directory not found: {source_dir}")
        
        # Handle different stem configurations
        if stem_number == 2:
            # Create vocals and no_vocals (accompaniment) stems
            vocals_path = os.path.join(source_dir, "vocals.wav")
            
            # Generate enhanced filenames
            if analyze_features and bpm is not None and key is not None:
                vocals_filename = generate_filename_with_features("vocals.wav", bpm, key)
                no_vocals_filename = generate_filename_with_features("no_vocals.wav", bpm, key)
            else:
                vocals_filename = "vocals.wav"
                no_vocals_filename = "no_vocals.wav"
            
            # Copy vocals
            if os.path.exists(vocals_path):
                shutil.copy(vocals_path, os.path.join(output_dir, vocals_filename))
                print(f"✓ Created {vocals_filename}")
            
            # Create no_vocals by mixing drums, bass, and other
            try:
                import soundfile as sf
                import numpy as np
                
                drums_path = os.path.join(source_dir, "drums.wav")
                bass_path = os.path.join(source_dir, "bass.wav")
                other_path = os.path.join(source_dir, "other.wav")
                
                # Read all accompaniment stems
                drums, sr = sf.read(drums_path)
                bass, _ = sf.read(bass_path)
                other, _ = sf.read(other_path)
                
                # Mix them together
                no_vocals = drums + bass + other
                
                # Write the mixed accompaniment
                no_vocals_path = os.path.join(output_dir, no_vocals_filename)
                sf.write(no_vocals_path, no_vocals, sr)
                print(f"✓ Created {no_vocals_filename}")
                
            except Exception as e:
                print(f"Warning: Could not create no_vocals stem: {str(e)}")
        
        else:  # stem_number == 4 (default)
            # Copy all 4 stems
            stem_files = ["vocals.wav", "drums.wav", "bass.wav", "other.wav"]
            
            for stem_file in stem_files:
                src_path = os.path.join(source_dir, stem_file)
                
                if os.path.exists(src_path):
                    # Generate enhanced filename with BPM and key if analysis was successful
                    if analyze_features and bpm is not None and key is not None:
                        enhanced_filename = generate_filename_with_features(stem_file, bpm, key)
                        dst_path = os.path.join(output_dir, enhanced_filename)
                    else:
                        dst_path = os.path.join(output_dir, stem_file)
                    
                    # Copy each stem file to the output directory
                    shutil.copy(src_path, dst_path)
                    print(f"✓ Created {os.path.basename(dst_path)}")
        
        # Clean up temp directory
        shutil.rmtree(temp_output, ignore_errors=True)
        
        if analyze_features and bpm is not None and key is not None:
            print(f"✅ Audio successfully split into {stem_number} stems with features ({bpm} BPM, {key})")
        else:
            print(f"✅ Audio successfully split into {stem_number} stems")
        
        return output_dir
        
    except Exception as e:
        # Clean up temp directory on error
        shutil.rmtree(temp_output, ignore_errors=True)
        raise Exception(f"Error during stem extraction: {str(e)}")

