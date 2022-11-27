from django.urls import re_path, path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import AllowAny
from rest_framework.routers import DefaultRouter

from api.v1.endpoints import SongViewSet


router = DefaultRouter()
router.register(r'songs', SongViewSet, basename='songs')

app_name = 'v1'

schema_view_api_v1 = get_schema_view(
        openapi.Info(
                title="Sound Check API backend",
                default_version='v1',
                description="Sound Check API",
                terms_of_service="https://www.google.com/policies/terms/",
                contact=openapi.Contact(email="contact@snippets.local"),
                license=openapi.License(name="BSD License"),
        ),
        public=True,
        permission_classes=(AllowAny,),
)

urlpatterns = [

    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view_api_v1.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view_api_v1.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view_api_v1.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    path('', include(router.urls)),

]
