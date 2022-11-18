from core.models import Song, Fingerprint


# ========== QUERIES FOR SONGS ==========
def insert_song(file_path, song_filename, file_sha1):
    return Song.objects.create(file_path=file_path, song_filename=song_filename, file_sha1=file_sha1).id


def get_song_by_id(song_id):
    return Song.objects.get(id=song_id)


def get_songs_by_ids(ids):
    return Song.objects.filter(id__in=ids, fingerprinted=True)


def set_song_fingerprinted(song_id):
    Song.objects.filter(id=song_id).update(fingerprinted=True)


def get_fingerprinted_songs():
    return set(map(bytes, Song.objects.filter(fingerprinted=True).values_list("file_sha1", flat=True)))


def delete_unfingerprinted_songs():
    Song.objects.filter(fingerprinted__isnull=True).delete()


def get_num_songs():
    return Song.objects.all().count()


# ========== QUERIES FOR FINGERPRINTS ==========

def insert_fingerprint(hash_sum, sid, time_offset):
    Fingerprint.objects.create(hash_sum=hash_sum, song=sid, time_offset=time_offset)


def insert_hashes(song, hashes):
    fingerprints = []
    for hash_sum, time_offset in hashes:
        fingerprints.append(Fingerprint(hash_sum=hash_sum, time_offset=time_offset, song_id=song))
    Fingerprint.objects.bulk_create(fingerprints)


def get_num_fingerprints():
    return Fingerprint.objects.all().count()


def query(hash_sum):
    if hash_sum:
        fingerprints = Fingerprint.objects.filter(hash_sum=hash_sum)
    else:
        fingerprints = Fingerprint.objects.all()
    return fingerprints


def return_matches(hashes):
    hash_list = [i[0] for i in list(hashes)]
    return Fingerprint.objects.filter(hash_sum__in=hash_list).values_list("song_id", "time_offset", "hash_sum")
