from drf_yasg.utils import swagger_auto_schema
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from api.v1.pagination import StandardResultsSetPagination
from api.v1.serializers import SongCreateSerializer, FindSimilarSongSerializer, SimilarSongSerializer
from core.models import Song


class SongViewSet(ModelViewSet):
    serializer_class = SongCreateSerializer
    pagination_class = StandardResultsSetPagination
    filterset_fields = ["author", "song_name", "time_create", "time_update"]


    @swagger_auto_schema(request_body=FindSimilarSongSerializer())
    @action(methods=['POST'], detail=False, url_path="find_similar", serializer_class=FindSimilarSongSerializer)
    def find_similar(self, request):
        serializer = FindSimilarSongSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        songs = serializer.save()
        serializer = SimilarSongSerializer(songs, many=True)
        return Response(status=200, data=serializer.data)


    def get_queryset(self):
        return Song.objects.all()
