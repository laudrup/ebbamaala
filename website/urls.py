from markdownx import urls as markdownx
from django.urls import path, include
from django.conf import settings

from . import views

app_name = 'website'
urlpatterns = [
    path('', views.index, name='index'),
    path('info', views.info, name='info'),
    path('markdownx/', include(markdownx)),
]

if not settings.DEBUG:
    urlpatterns += path('media/<filename>', views.media, name='media')
