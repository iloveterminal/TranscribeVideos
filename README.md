# TranscribeVideos
A simple Python script to recursively iterate a given local directory, find all matching audio/video files based on given extensions, and transcribe them to English text using faster-whisper (https://github.com/SYSTRAN/faster-whisper).

For each audio/video file processed a text file is created with a default suffix of '_auto_transcript.txt' in the same directory as the file.

Re-runs of this script will ignore files where a transcript already exists.

## Requirements

* Python 3.8 or greater
* faster-whisper (https://github.com/SYSTRAN/faster-whisper)
* python-dotenv

## Usage

First copy '.env.example' to '.env' and modify the variables as appropriate.

Then, from a terminal in the root directory of the project simply run `python3 TranscribeVideos.py`. That's it!

NOTE: depending on the RAM available on your machine, larger videos could cause the script to die prematurely. Simply re-run the script and it will pick up where it left off, this time skipping the problem video. Creating an empty file with a suffix of '_auto_transcript.txt' is an easy way to exclude any large videos from processing.