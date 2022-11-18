import multiprocessing as mp
import os
import sys
import traceback
from collections import Counter

from core import constants, file_utils, fingerprint_utils
from core.views import db_views


class SoundCheck(object):

    def __init__(self):
        self.limit = constants.FINGERPRINT_LIMIT
        self.songs_sha1_set = db_views.get_fingerprinted_songs()
        db_views.delete_unfingerprinted_songs()

    def fingerprint_directory(self, path, extensions, num_processes=None):
        try:
            num_processes = num_processes or mp.cpu_count()
        except NotImplementedError:
            num_processes = 1
        else:
            num_processes = 1 if num_processes <= 0 else num_processes

        pool = mp.Pool(num_processes)

        filenames_to_fingerprint = []
        if len(self.songs_sha1_set) != 0:
            for filename in file_utils.crawl_directory(path, extensions):

                # skip fingerprinted file
                if file_utils.get_file_hash(filename) in self.songs_sha1_set:
                    print("%s already fingerprinted, continuing..." % filename)
                    continue

                filenames_to_fingerprint.append(filename)
        else:
            filenames_to_fingerprint.extend(list(file_utils.crawl_directory(path, extensions)))

        worker_input = zip(filenames_to_fingerprint,
                           [self.limit] * len(filenames_to_fingerprint))

        iterator = pool.imap_unordered(_fingerprint_worker,
                                       worker_input)

        while True:
            try:
                file_path, song_name, hashes, file_hash = iterator.next()
            except mp.TimeoutError:
                continue
            except StopIteration:
                break
            except:
                print("Failed fingerprinting")
                traceback.print_exc(file=sys.stdout)
            else:
                sid = db_views.insert_song(file_path, song_name, file_hash)
                db_views.insert_hashes(sid, hashes)
                db_views.set_song_fingerprinted(sid)
                self.songs_sha1_set = db_views.get_fingerprinted_songs()

        pool.close()
        pool.join()

    def fingerprint_file(self, filepath, song_name=None):
        file_utils.check_file(filepath)
        songname = file_utils.get_filename(filepath)
        song_hash = file_utils.get_file_hash(filepath)
        song_name = song_name or songname
        if song_hash in self.songs_sha1_set:
            print("%s already fingerprinted, continuing..." % song_name)
        else:
            _, song_name, hashes, file_hash = _fingerprint_worker(
                filepath,
                self.limit,
                song_name=song_name
            )
            sid = db_views.insert_song(filepath, song_name, file_hash)

            db_views.insert_hashes(sid, hashes)
            db_views.set_song_fingerprinted(sid)
            self.songs_sha1_set = db_views.get_fingerprinted_songs()

    def find_matches(self, sample_data, top_limit=10, sr=constants.DEFAULT_SAMPLE_RATE):
        song_offsets = {}
        song_max_offsets = []

        hashes = list(fingerprint_utils.fingerprint(sample_data, sr=sr))
        matches = db_views.return_matches(hashes)
        hashes = dict(hashes)

        for sid, offset, hash_sum in matches:
            if sid in song_offsets:
                song_offsets[sid].append(offset - hashes[hash_sum.tobytes()])
            else:
                song_offsets[sid] = [offset - hashes[hash_sum.tobytes()]]

        for k, v in song_offsets.items():
            song_max_offsets.append((k, sum([i[1] for i in Counter(v).most_common(3)])))
        song_max_offsets = sorted(song_max_offsets, key=lambda i: i[1], reverse=True)[:top_limit]
        ids = [i[0] for i in song_max_offsets]

        songs = db_views.get_songs_by_ids(ids)
        songs = dict([(song.id, song) for song in songs])
        songs = [(songs[i].song_filename, songs[i].file_path) for i in ids]

        return songs

    def recognize(self, recognizer, *options, **kwoptions):
        r = recognizer(self)
        return r.recognize(*options, **kwoptions)


def _fingerprint_worker(filename, limit=None, song_name=None):
    try:
        filename, limit = filename
    except ValueError:
        pass

    songname, extension = os.path.splitext(os.path.basename(filename))
    song_name = song_name or songname
    sound, file_hash = file_utils.read_file(filename, limit)
    result = set()

    print("Fingerprinting  %s" % filename)
    hashes = fingerprint_utils.fingerprint(sound, sr=constants.DEFAULT_SAMPLE_RATE)
    print("Fingerprinting finished for %s" % filename)
    result |= set(hashes)

    return filename, song_name, result, file_hash
