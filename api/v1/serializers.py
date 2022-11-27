from rest_framework.fields import BooleanField, DateTimeField, FileField
from rest_framework.serializers import ModelSerializer, Serializer

from core.models import Song


class SongCreateSerializer(ModelSerializer):
    fingerprinted = BooleanField(read_only=True)
    time_create = DateTimeField(read_only=True)
    time_update = DateTimeField(read_only=True)


    def create(self, validated_data):
        song = super().create(validated_data)
        # TODO: start fingerprints extraction
        return song


    def update(self, instance, validated_data):
        instance.author = validated_data.get("author", instance.author)
        instance.song_name = validated_data.get("song_name", instance.song_name)
        instance.save()
        return instance


    class Meta:
        model = Song
        fields = ["id", "author", "song_name", "file", "fingerprinted", "time_create", "time_update"]


class FindSimilarSongSerializer(Serializer):
    file = FileField()


    def update(self, instance, validated_data):
        pass


    def create(self, validated_data):
        # file = validated_data.pop('file')
        pass  # TODO: perform find similar
