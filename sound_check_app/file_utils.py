import os
from hashlib import sha1

import librosa

from sound_check_app import constants


def get_file_hash(filepath, block_size=2 ** 20):
    s = sha1()
    with open(filepath, "rb") as f:
        while True:
            buf = f.read(block_size)
            if not buf:
                break
            s.update(buf)
    return s.digest()


def crawl_directory(path, extensions):
    if not os.path.isdir(path):
        raise Exception("Not a directory.<br>Please, provide path to directory")

    extensions = tuple(extensions)
    for dir_path, dir_names, files in os.walk(path):
        for filename in [f for f in files if f.lower().endswith(extensions)]:
            p = os.path.join(dir_path, filename)
            yield p


def check_file(filepath):
    if os.path.isdir(filepath):
        raise Exception("Not a filepath.<br>Please, provide path to the file")
    if not filepath.lower().endswith(tuple(("mp3", "wav"))):
        raise Exception("Unknown file extension.<br>Available 'mp3' and 'wav'.")


def read_file(filename, sample_rate=constants.DEFAULT_SAMPLE_RATE, limit=None):
    sound, _ = librosa.load(filename, sample_rate)
    if limit:
        sound = sound[:limit * 1000]
    return sound, get_file_hash(filename)


def get_filename(path):
    return os.path.splitext(os.path.basename(path))[0]
