import os
from collections import Counter
from hashlib import sha256

import librosa
import numpy as np
from scipy import ndimage

from core.models import Song, Fingerprint
from core.settings import DEFAULT_SAMPLE_RATE, FINGERPRINT_LIMIT, PEAK_NEIGHBORHOOD_SIZE, PEAK_SORT, DEFAULT_TIME_RESOLUTION, FINGERPRINT_REDUCTION
from sound_check.settings import MEDIA_ROOT


class SongService:

    @staticmethod
    def run_main_work(pk):
        song = Song.objects.get(pk=pk)
        song.song_status = Song.SongStatus.IN_PROGRESS
        song.save(update_fields=['song_status'])
        file_path = SongService.get_file_path(song)
        data = SongService.__read_file_for_creating_fingerprints(file_path)
        fingerprints = SongService.__create_song_fingerprint_objects(data, song)
        Fingerprint.objects.bulk_create(fingerprints)
        song.song_status = Song.SongStatus.FINGERPRINTS_CREATED
        song.save(update_fields=['song_status'])


    @staticmethod
    def find_similar_songs(file, top_limit=1):
        file_path = file.temporary_file_path()
        data = SongService.__read_file_for_creating_fingerprints(file_path)
        fingerprints = dict(SongService.__create_song_fingerprints(data))
        matches = Fingerprint.objects.filter(hash_sum__in=fingerprints.keys()).values_list("song_id", "time_offset", "hash_sum")
        song_offsets = {}
        song_max_offsets = []

        for sid, offset, hash_sum in matches:
            if sid in song_offsets:
                song_offsets[sid].append(offset - fingerprints[hash_sum])
            else:
                song_offsets[sid] = [offset - fingerprints[hash_sum]]

        for k, v in song_offsets.items():
            song_max_offsets.append((k, sum([i[1] for i in Counter(v).most_common(3)])))
        song_max_offsets = sorted(song_max_offsets, key=lambda i: i[1], reverse=True)[:top_limit]
        ids = [i[0] for i in song_max_offsets]

        return Song.objects.filter(id__in=ids)  # TODO: preserve order


    @staticmethod
    def get_file_path(song):
        return os.path.join(MEDIA_ROOT, song.file.name)


    @staticmethod
    def is_file_in_library(hash_sum):
        return Song.objects.filter(file_sha256=hash_sum).exists()


    @staticmethod
    def get_file_hash(file_path, block_size=2 ** 20):
        s = sha256()
        with open(file_path, "rb") as f:
            while True:
                buf = f.read(block_size)
                if not buf:
                    break
                s.update(buf)
        return s.hexdigest()


    @staticmethod
    def __read_file_for_creating_fingerprints(file_path):
        sound, _ = librosa.load(file_path, sr=DEFAULT_SAMPLE_RATE)
        if FINGERPRINT_LIMIT:
            sound = sound[:FINGERPRINT_LIMIT * 1000]
        return sound


    @staticmethod
    def __create_song_fingerprints(data):
        y = librosa.power_to_db(S=librosa.feature.melspectrogram(y=data, sr=DEFAULT_SAMPLE_RATE, n_mels=128), ref=np.max)
        peeks = SongService.__get_spectrogram_peaks(y)
        return SongService.__generate_fingerprints(peeks)


    @staticmethod
    def __create_song_fingerprint_objects(data, song):
        y = librosa.power_to_db(S=librosa.feature.melspectrogram(y=data, sr=DEFAULT_SAMPLE_RATE, n_mels=128), ref=np.max)
        peeks = SongService.__get_spectrogram_peaks(y)
        return SongService.__generate_fingerprint_objects(peeks, song)


    @staticmethod
    def __get_spectrogram_peaks(spectrogram):
        peeks = ndimage.filters.maximum_filter(spectrogram, PEAK_NEIGHBORHOOD_SIZE) == spectrogram
        labels, num_features = ndimage.label(peeks)
        objs = ndimage.find_objects(labels)
        points = []
        for dy, dx in objs:
            x_center = (dx.start + dx.stop - 1) // 2
            y_center = (dy.start + dy.stop - 1) // 2
            if (dx.stop - dx.start) * (dy.stop - dy.start) == 1:
                points.append((x_center, y_center))

        if PEAK_SORT:
            points = sorted(points)
        return points


    @staticmethod
    def __find_neighbors(collection, window):
        neighbors = []
        for p in collection:
            if window[0] < p[0] < window[1] and window[2] < p[1] < window[3]:
                neighbors.append(p)
        return neighbors


    @staticmethod
    def __generate_fingerprints(peaks):
        target = (int(1 / DEFAULT_TIME_RESOLUTION), int(5 / DEFAULT_TIME_RESOLUTION), -50, 50)
        for point in peaks:
            window = (point[0] + target[0], point[0] + target[1], point[1] + target[2], point[1] + target[3])
            neighbors = SongService.__find_neighbors(peaks, window)

            for n in neighbors:
                line = f"{point[1]}|{n[1]}|{n[0] - point[0]}"
                h = sha256(line.encode('utf-8'))
                yield h.hexdigest()[0:FINGERPRINT_REDUCTION], point[0]


    @staticmethod
    def __generate_fingerprint_objects(peaks, song):
        fingerprints = []
        for hash_sum, offset in SongService.__generate_fingerprints(peaks):
            fingerprints.append(Fingerprint(hash_sum=hash_sum, time_offset=offset, song=song))
        return fingerprints
