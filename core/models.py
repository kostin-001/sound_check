from django.db import models
from django.utils.translation import gettext_lazy as _


class Song(models.Model):
    class SongStatus(models.TextChoices):
        BRAND_NEW = ('BN', _('BRAND NEW'))
        IN_PROGRESS = ('IP', _('IN PROGRESS'))
        FINGERPRINTS_CREATED = ('FC', _('FINGERPRINTS CREATED'))
        ERROR = ('ER', _('ERROR'))


    author = models.CharField(max_length=250, verbose_name="Автор")
    song_name = models.CharField(max_length=250, verbose_name="Название")
    song_status = models.CharField(choices=SongStatus.choices, max_length=2, default=SongStatus.BRAND_NEW)
    file_sha256 = models.CharField(max_length=256, verbose_name="Хеш-сумма")
    time_create = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    time_update = models.DateTimeField(auto_now=True, verbose_name="Время создания")
    file = models.FileField(upload_to="music_library/", verbose_name="Файл")


    def __str__(self):
        return f"{self.author} - {self.song_name}"


    class Meta:
        indexes = [
            models.Index(fields=['author']),
            models.Index(fields=['song_name']),
            models.Index(fields=['file_sha256']),
        ]


class Fingerprint(models.Model):
    hash_sum = models.CharField(max_length=256, verbose_name="Хеш-сумма")
    time_offset = models.IntegerField(verbose_name="Сдвиг от начала")
    song = models.ForeignKey(Song, on_delete=models.CASCADE, verbose_name="Связанный звуковой файл")


    class Meta:
        unique_together = ['hash_sum', 'song', 'time_offset']
        indexes = [
            models.Index(fields=['hash_sum']),
        ]
