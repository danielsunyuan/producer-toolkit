from spleeter.separator import Separator
import os

def extract_stems(audio_path, output_dir, stem_number=2):
    """
    Splits the audio file into stems using Spleeter.

    Args:
        audio_path (str): Path to the input audio file (should be .wav).
        output_dir (str): Directory where the separated stems will be saved.
        stem_number (int): Number of stems (2, 4, or 5). Default is 2 stems.

    Returns:
        str: The path to the directory where stems are saved.
    """
    # Get the file name without extension to set the output directory
    file_name = os.path.splitext(os.path.basename(audio_path))[0]

    # Use output_dir directly without creating a subdirectory with file_name
    output_stem_dir = os.path.join(output_dir)

    # Initialize Spleeter with the specified number of stems
    separator = Separator(f'spleeter:{stem_number}stems')

    # Perform the audio separation, saving results in output_dir, avoiding nested folders
    separator.separate_to_file(audio_path, output_stem_dir)

    print(f"Audio successfully split into {stem_number} stems at {output_stem_dir}")
    return output_stem_dir

if __name__ == "__main__":
    # Example Usage
    audio = "/Users/duan/Documents/Producer Toolkit/loading/Yee.wav"
    dir = "/Users/duan/Documents/Producer Toolkit/loading/"
    out = extract_stems(audio, dir)
    print()
    print(out)