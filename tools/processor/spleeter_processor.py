import os
from spleeter.separator import Separator

def extract_stems(audio_path, output_dir, stem_number=2):
    """
    Splits the audio file into stems using Spleeter.
    
    Args:
        audio_path (str): Path to the input audio file (WAV format expected).
        output_dir (str): Directory where the separated stems will be saved.
        stem_number (int): Number of stems (e.g., 2, 4, or 5). Default is 2 stems.
    
    Returns:
        str: The output directory where stems are saved.
    """
    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize Spleeter with the specified number of stems.
    separator = Separator(f'spleeter:{stem_number}stems')
    
    # Perform separation; Spleeter will create subdirectories inside output_dir.
    separator.separate_to_file(audio_path, output_dir)
    
    print(f"✅ Audio successfully split into {stem_number} stems at {output_dir}")
    return output_dir
