from django.db import models


class Song(models.Model):
    song_filename = models.CharField(max_length=250)
    fingerprinted = models.BooleanField(default=False)
    file_sha1 = models.BinaryField()
    file_path = models.CharField(max_length=1024)


class Fingerprint(models.Model):
    hash_sum = models.BinaryField()
    song = models.ForeignKey(Song, on_delete=models.CASCADE)
    time_offset = models.IntegerField()

    class Meta:
        unique_together = ['hash_sum', 'song', 'time_offset']
        indexes = [
            models.Index(fields=['hash_sum']),
        ]
