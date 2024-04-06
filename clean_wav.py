from glob import glob
from argparse import ArgumentParser
from pprint import pprint
from os.path import basename, expanduser, join as path_join
from subprocess import run, CalledProcessError
from pathlib import Path


source_path = expanduser("~/Downloads/bandcamp_collection_wav_bak/bandcamp_collection_wav")
dest_path = expanduser("~/Desktop/bandcamp_processed_wav")

incomplete_files = glob(path_join(source_path, '**', '*download'), recursive=True)
all_wav_files = glob(path_join(source_path, '**', '*wav'), recursive=True)

complete_wav_files = [
            x for x in all_wav_files if not any(x in string for string in incomplete_files)
        ]

for file in complete_wav_files:
    filename = basename(file)

    try:
        res = run(
            [
                "/opt/homebrew/bin/ffmpeg",
                "-y", "-loglevel", "error",
                "-i", file, f"{dest_path}/{filename}"
            ],
            shell=False, check=True, capture_output=True
        )

        print(f"Processed {filename}")

    except CalledProcessError as cpe:
        print(f"[ERROR] Failed processing file {filename}")
        print(f"stderr: {cpe.stderr.decode('utf-8')}\n")
