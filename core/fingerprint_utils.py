import hashlib

import librosa
import numpy as np
from scipy import ndimage
from scipy.ndimage.filters import maximum_filter

from core import constants


def fingerprint(data, sr=constants.DEFAULT_SAMPLE_RATE):
    y = librosa.power_to_db(librosa.feature.melspectrogram(data, sr=sr, n_mels=128), ref=np.max)
    peeks = get_spectrogram_peaks(y)
    return generate_hashes(peeks)


def get_spectrogram_peaks(spectrogram):
    peeks = maximum_filter(spectrogram, constants.PEAK_NEIGHBORHOOD_SIZE) == spectrogram

    labels, num_features = ndimage.label(peeks)
    objs = ndimage.find_objects(labels)
    points = []
    for dy, dx in objs:
        x_center = (dx.start + dx.stop - 1) // 2
        y_center = (dy.start + dy.stop - 1) // 2
        if (dx.stop - dx.start) * (dy.stop - dy.start) == 1:
            points.append((x_center, y_center))

    if constants.PEAK_SORT:
        points = sorted(points)
    return points


def find_neighbors(collection, window):
    neighbors = []
    for p in collection:
        if window[0] < p[0] < window[1] and window[2] < p[1] < window[3]:
            neighbors.append(p)
    return neighbors


def generate_hashes(peaks):
    target = (int(1 / constants.DEFAULT_TIME_RESOLUTION), int(5 / constants.DEFAULT_TIME_RESOLUTION), -50, 50)
    for point in peaks:
        window = (point[0] + target[0], point[0] + target[1], point[1] + target[2], point[1] + target[3])
        neighbors = find_neighbors(peaks, window)

        for n in neighbors:
            line = "{}|{}|{}".format(str(point[1]), str(n[1]), str(n[0] - point[0]))
            h = hashlib.sha1(line.encode('utf-8'))
            yield h.digest()[0:constants.FINGERPRINT_REDUCTION], point[0]
