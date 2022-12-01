from collections import Counter
from hashlib import sha256

import librosa
import numpy as np
from scipy import ndimage

from core.models import Song, Fingerprint
from core.settings import DEFAULT_SAMPLE_RATE, FINGERPRINT_LIMIT, PEAK_NEIGHBORHOOD_SIZE, PEAK_SORT, DEFAULT_TIME_RESOLUTION, FINGERPRINT_REDUCTION


class SongService:
    """
    Main class to interact with audio files and it's fingerprints creation.
    The nature of fingerprints is just a hashes from string p1, p2, p2-p1 (where p1 and p2 are peak points in moving windows on spectrogram).
    """


    @staticmethod
    def run_main_work(pk: int):
        """
            Entry point for creating audio fingerprints

        :param pk: pk of new song object
        :return:
            creates fingerprints and save them into database
        """
        song = Song.objects.get(pk=pk)
        song.song_status = Song.SongStatus.IN_PROGRESS
        song.save(update_fields=['song_status'])
        file_path = SongService.get_file_path(song.file)
        data = SongService.__read_file_for_creating_fingerprints(file_path)
        fingerprints = SongService.__create_song_fingerprint_objects(data, song)
        Fingerprint.objects.bulk_create(fingerprints)
        song.song_status = Song.SongStatus.FINGERPRINTS_CREATED
        song.save(update_fields=['song_status'])


    @staticmethod
    def find_similar_songs(file, top_limit: int = 1):
        """
            Entry point for searching similar song objects based on audio fingerprints similarity

        :param file: TemporaryUploadedFile  - file for which it is needed to find similar songs
        :param top_limit: int - maximum number of similar items to return
        :return: QuerySet - list of similar songs
        """
        file_path = file.temporary_file_path()
        data = SongService.__read_file_for_creating_fingerprints(file_path)
        fingerprints = dict(SongService.__create_song_fingerprints(data))
        matches = Fingerprint.objects.filter(hash_sum__in=fingerprints.keys()).values_list("song_id", "time_offset", "hash_sum")
        song_offsets = {}

        for sid, offset, hash_sum in matches:
            if sid in song_offsets:
                song_offsets[sid].append(offset - fingerprints[hash_sum])
            else:
                song_offsets[sid] = [offset - fingerprints[hash_sum]]

        total_sum = 0
        for k, v in song_offsets.items():
            current_sum = sum([i[1] for i in Counter(v).most_common(3)])
            song_offsets[k] = current_sum
            total_sum += current_sum

        for k, v in song_offsets.items():
            song_offsets[k] = song_offsets[k] / total_sum * 100

        song_max_offsets = sorted(song_offsets.items(), key=lambda i: i[1], reverse=True)[:top_limit]
        ids = [i[0] for i in song_max_offsets]
        songs = []
        for song in Song.objects.filter(id__in=ids):
            song.similarity = song_offsets.get(song.pk)
            songs.append(song)

        songs.sort(key=lambda x: x.similarity, reverse=True)
        return songs


    @staticmethod
    def get_file_path(file):
        return file.temporary_file_path()


    @staticmethod
    def is_file_in_library(hash_sum: str):
        return Song.objects.filter(file_sha256=hash_sum).exists()


    @staticmethod
    def get_file_hash(file_path: str, block_size: int = 2 ** 20):
        s = sha256()
        with open(file_path, "rb") as f:
            while True:
                buf = f.read(block_size)
                if not buf:
                    break
                s.update(buf)
        return s.hexdigest()


    @staticmethod
    def __read_file_for_creating_fingerprints(file_path: str):
        """
            Method for opening file exactly as audio file (floating point time series)

        :param file_path: str - path to audio file
        :return: np.ndarray - floating point time series
        """
        sound, _ = librosa.load(file_path, sr=DEFAULT_SAMPLE_RATE)
        if FINGERPRINT_LIMIT:
            sound = sound[:FINGERPRINT_LIMIT * 1000]
        return sound


    @staticmethod
    def __create_song_fingerprints(data):
        """
            Wrapper method for creating audio file fingerprints pipeline

        :param data: np.ndarray - floating point time series
        :return: generator of fingerprints
        """
        y = librosa.power_to_db(S=librosa.feature.melspectrogram(y=data, sr=DEFAULT_SAMPLE_RATE, n_mels=128), ref=np.max)
        peeks = SongService.__get_spectrogram_peaks(y)
        return SongService.__generate_fingerprints(peeks)


    @staticmethod
    def __create_song_fingerprint_objects(data, song: Song):
        """
            Wrapper method for creating fingerprint objects (to save in database) pipeline

        :param data: np.ndarray - floating point time series
        :param song: Song object
        :return: list of Fingerprint objects
        """
        y = librosa.power_to_db(S=librosa.feature.melspectrogram(y=data, sr=DEFAULT_SAMPLE_RATE, n_mels=128), ref=np.max)
        peeks = SongService.__get_spectrogram_peaks(y)
        return SongService.__generate_fingerprint_objects(peeks, song)


    @staticmethod
    def __get_spectrogram_peaks(spectrogram):
        """
            Method for calculating peaks from dB spectrogram

        :param spectrogram: np.ndarray
        :return: np.ndarray - list of peaks
        """
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
        """
            Method for finding neighbor points for given window

        :param collection: np.ndarray - peaks
        :param window: tuple - 4 points (2-dimensional window)
        :return: list of neighbors (anchor points)
        """
        neighbors = []
        for p in collection:
            if window[0] < p[0] < window[1] and window[2] < p[1] < window[3]:
                neighbors.append(p)
        return neighbors


    @staticmethod
    def __generate_fingerprints(peaks):
        """
            Method for creating fingerprints

        :param peaks: np.ndarray - spectrogram peaks
        :return: fingerprints generator
        """
        target = (int(1 / DEFAULT_TIME_RESOLUTION), int(5 / DEFAULT_TIME_RESOLUTION), -50, 50)  # start, end, Hz low, Hz high - window itself
        for point in peaks:
            window = (point[0] + target[0], point[0] + target[1], point[1] + target[2], point[1] + target[3])
            neighbors = SongService.__find_neighbors(peaks, window)

            for n in neighbors:
                line = f"{point[1]}|{n[1]}|{n[0] - point[0]}"
                h = sha256(line.encode('utf-8'))
                yield h.hexdigest()[0:FINGERPRINT_REDUCTION], point[0]


    @staticmethod
    def __generate_fingerprint_objects(peaks, song: Song):
        """
            Method for creating Fingerprint objects

        :param peaks: np.ndarray - spectrogram peaks
        :param song: Song object
        :return: list of Fingerprint objects
        """
        fingerprints = []
        for hash_sum, offset in SongService.__generate_fingerprints(peaks):
            fingerprints.append(Fingerprint(hash_sum=hash_sum, time_offset=offset, song=song))
        return fingerprints
