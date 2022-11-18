"""sound_check URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from core.views import front_views

urlpatterns = [
    path('do_crawl/', front_views.do_crawl, name='do_crawl'),
    path('add_to_index/', front_views.add_to_index, name='add_to_index'),
    path('find_similar/', front_views.find_similar, name='find_similar'),
    path('index/', front_views.index, name='index'),
    path('similar/', front_views.similar_page, name='similar_page'),
    path('', front_views.index, name='index'),
    path('admin/', admin.site.urls),
]
