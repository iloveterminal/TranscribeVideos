"""TranscribeVideos

This script will recursively iterate a given local directory,
find all matching audio/video files based on given extensions,
and transcribe them to English text using faster-whisper.

For each audio/video file processed a text file is created with a
default suffix of '_auto_transcript.txt' in the same directory as the file.

Re-runs of this script will ignore files where a transcript already exists.
"""

import json
import os

from datetime import datetime
from dotenv import load_dotenv
from faster_whisper import WhisperModel


def run_fast_scandir(directory, ext):  # directory: str, ext: list
    """Recursively find all files matching given extension(s).

    Args:
        directory (str): Full path to the initial root directory to scan.
        ext (list): A list of audio/video file extensions to include.

    Returns:
        subfolders: A list of the subfolders.
        files: A list of the matching files.
    """
    subfolders, files = [], []

    for f in os.scandir(directory):
        if f.is_dir():
            subfolders.append(f.path)
        if f.is_file():
            if os.path.splitext(f.name)[1].lower() in ext:
                # Ignore hidden files.
                if not f.name.startswith('.'):
                    files.append(f.path)

    for directory in list(subfolders):
        sf, f = run_fast_scandir(directory, ext)
        subfolders.extend(sf)
        files.extend(f)
    return subfolders, files


load_dotenv()
if 'AUDIO_VIDEO_PATH' not in os.environ:
    print('Please ensure .env file exists with "AUDIO_VIDEO_PATH" defined.')
if 'INCLUDE_EXTENSIONS' not in os.environ:
    print('Please ensure .env file exists with "INCLUDE_EXTENSIONS" defined.')
video_path = os.getenv('AUDIO_VIDEO_PATH')
include_extensions = json.loads(os.getenv('INCLUDE_EXTENSIONS'))
datetime_format = '%Y-%m-%d %H:%M:%S'
all_subfolders, all_files = run_fast_scandir(video_path, include_extensions)
# WARNING: changing transcript_suffix could cause re-processing of previously completed files.
transcript_suffix = os.getenv('TRANSCRIPT_SUFFIX', '_auto_transcript.txt')

for file in all_files:
    try:
        filename = os.path.basename(file)
        directory_path = os.path.dirname(file)
        filename_no_extension = os.path.splitext(filename)[0]
        transcript_filename = directory_path + '/' + filename_no_extension + transcript_suffix
        if not os.path.exists(transcript_filename):
            print('\n' + file)
            print('Start: ' + datetime.now().strftime(datetime_format))
            transcript_file = open(transcript_filename, 'w')
            model = WhisperModel(
                compute_type='float32',
                device='cpu',
                model_size_or_path='small.en'
            )
            segments, info = model.transcribe(file, language='en', beam_size=2)
            all_text = ''
            for segment in segments:
                all_text += segment.text
            # Format text with each sentence on a new line for readability.
            all_text = all_text.lstrip()
            all_text = all_text.replace('. ', '.\n')
            all_text = all_text.replace('? ', '?\n')
            all_text = all_text.replace('! ', '!\n')
            # Remove new lines where not actually the end of a sentence.
            all_text = all_text.replace('Dr.\n', 'Dr. ')
            all_text = all_text.replace('dr.\n', 'dr. ')
            all_text = all_text.replace('Mr.\n', 'Mr. ')
            all_text = all_text.replace('mr.\n', 'mr. ')
            all_text = all_text.replace('Mrs.\n', 'Mrs. ')
            all_text = all_text.replace('mrs.\n', 'mrs. ')
            all_text = all_text.replace('Ms.\n', 'Ms. ')
            all_text = all_text.replace('ms.\n', 'ms. ')
            all_text = all_text.replace(' p.\nm', ' p.m')
            all_text = all_text.replace(' p.m.\n', ' p.m. ')
            all_text = all_text.replace(' a.\nm', ' a.m')
            all_text = all_text.replace(' a.m.\n', ' a.m. ')
            all_text = all_text.replace('etc.\n,', 'etc.,')
            all_text = all_text.replace('.\ncom', '.com')
            all_text = all_text.replace('U.\nS.', 'U.S.')
            all_text = all_text.replace(' St.\n', ' St. ')
            transcript_file.write(all_text)
            transcript_file.close()
            print('End: ' + datetime.now().strftime(datetime_format))
        else:
            print('Transcript already exists for: ' + transcript_filename)
    except Exception as error:
        # Print any exceptions and continue to next file.
        print(error)
        continue

