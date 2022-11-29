from rest_framework.exceptions import ValidationError
from rest_framework.fields import CharField, DateTimeField, FileField
from rest_framework.serializers import ModelSerializer, Serializer

from core.models import Song
from core.song_serivice import SongService
from sound_check import settings
from sound_check.tasks import create_song_fingerprints


class SongCreateSerializer(ModelSerializer):
    song_status = CharField(read_only=True)
    time_create = DateTimeField(read_only=True)
    time_update = DateTimeField(read_only=True)


    def create(self, validated_data):
        song = super().create(validated_data)
        filepath = SongService.get_file_path(song)
        ext = filepath.lower().split(".")[-1]
        if ext not in ["mp3", "wav"]:
            raise ValidationError(f"Unacceptable audio format. Expected mp3 or wav, got {ext}")
        hash_sum = SongService.get_file_hash(filepath)
        if SongService.is_file_in_library(hash_sum):
            song.delete()
            raise ValidationError("File with this hash-sum already exist")
        song.file_sha256 = hash_sum
        song.save(update_fields=['file_sha256'])
        create_song_fingerprints.apply_async((song.pk,), retry=False, expires=120, ignore_result=True, queue=settings.CELERY_TASKS_QUEUE)
        return song


    def update(self, instance, validated_data):
        instance.author = validated_data.get("author", instance.author)
        instance.song_name = validated_data.get("song_name", instance.song_name)
        instance.save()
        return instance


    class Meta:
        model = Song
        fields = ["id", "author", "song_name", "file", "song_status", "time_create", "time_update"]


class FindSimilarSongSerializer(Serializer):
    author = CharField(read_only=True)
    song_name = CharField(read_only=True)
    file = FileField()


    def update(self, instance, validated_data):
        pass


    def create(self, validated_data):
        file = validated_data.pop('file')
        hash_sum = SongService.get_file_hash(file.temporary_file_path())
        if SongService.is_file_in_library(hash_sum):
            return Song.objects.filter(file_sha256=hash_sum)
        return SongService.find_similar_songs(file)
