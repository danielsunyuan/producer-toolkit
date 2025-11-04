import os
import sys
import shutil
import logging
from pathlib import Path
from ..analyzer.audio_analyzer import analyze_audio, generate_filename_with_features
from ..utils.loading import Spinner

# Set model path before importing Spleeter
# This ensures models will be downloaded to our custom directory
project_root = Path(__file__).parent.parent.parent
models_dir = os.path.join(project_root, "models")
os.makedirs(models_dir, exist_ok=True)
os.environ['MODEL_PATH'] = models_dir

# Reduce TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 0=debug, 1=info, 2=warning, 3=error
logging.getLogger('tensorflow').setLevel(logging.ERROR)

# Now import Spleeter after environment variables are set
from spleeter.separator import Separator

def extract_stems(audio_path, output_dir, stem_number=2, models_dir=None, analyze_features=True):
    """
    Splits the audio file into stems using Spleeter with BPM and key analysis.
    
    Args:
        audio_path (str): Path to the input audio file (WAV format expected).
        output_dir (str): Directory where the separated stems will be saved.
        stem_number (int): Number of stems (e.g., 2, 4, or 5). Default is 2 stems.
        models_dir (str, optional): Directory where Spleeter models should be stored.
                                   If None, defaults to 'models' in the project root.
        analyze_features (bool): Whether to analyze and include BPM/key in stem filenames (default: True).
    
    Returns:
        str: The output directory where stems are saved.
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Use the module-level models_dir as default
    if models_dir is None:
        models_dir = os.environ.get('MODEL_PATH')
    
    # Analyze audio features first if requested
    bpm, key = None, None
    analysis_spinner = None
    if analyze_features:
        try:
            analysis_spinner = Spinner("🎵 Analyzing audio features")
            analysis_spinner.start()
            bpm, key = analyze_audio(audio_path)
            analysis_spinner.stop(f"✅ Detected: {bpm} BPM, Key: {key}")
        except Exception as e:
            if analysis_spinner:
                analysis_spinner.stop()
            print(f"⚠️  Warning: Audio analysis failed ({str(e)}), proceeding without features")
            analyze_features = False
    
    # Initialize Spleeter with the specified number of stems
    spinner = Spinner("🔧 Processing stems with Spleeter")
    spinner.start()
    
    separator = Separator(
        f'spleeter:{stem_number}stems',
        multiprocess=True,  # Set to True for faster processing if your system supports it
        stft_backend="tensorflow"
    )
    
    # Create a temporary directory for initial output
    temp_output = os.path.join(output_dir, "_temp_spleeter")
    os.makedirs(temp_output, exist_ok=True)
    
    # Perform separation; Spleeter will create subdirectories inside temp_output
    separator.separate_to_file(audio_path, temp_output)
    spinner.stop()
    
    # Get the filename from the audio path
    filename = os.path.splitext(os.path.basename(audio_path))[0]
    
    # Move files from nested directory structure directly to output_dir
    source_dir = os.path.join(temp_output, filename)
    
    if os.path.exists(source_dir):
        for stem_file in os.listdir(source_dir):
            src_path = os.path.join(source_dir, stem_file)
            
            # Generate enhanced filename with BPM and key if analysis was successful
            if analyze_features and bpm is not None and key is not None:
                enhanced_filename = generate_filename_with_features(stem_file, bpm, key)
                dst_path = os.path.join(output_dir, enhanced_filename)
            else:
                dst_path = os.path.join(output_dir, stem_file)
            
            # Move each stem file to the output directory
            shutil.move(src_path, dst_path)
            print(f"  ✓ {os.path.basename(dst_path)}")
    
    # Clean up temp directory
    shutil.rmtree(temp_output, ignore_errors=True)
    
    if analyze_features and bpm is not None and key is not None:
        print(f"✅ Successfully split into {stem_number} stems ({bpm} BPM, {key})")
    else:
        print(f"✅ Successfully split into {stem_number} stems")
    return output_dir