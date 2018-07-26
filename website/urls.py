from markdownx import urls as markdownx
from django.urls import path, re_path, include
from django.conf import settings

from . import views

app_name = 'website'
urlpatterns = [
    path('', views.index, name='index'),
    path('info', views.info, name='info'),
    path('gallery', views.gallery, name='gallery'),
    path('gallery/<gallery_id>/', views.photos, name='photos'),
    path('calendar', views.calendar, name='calendar'),
    path('calendar/<int:year>/<int:month>/', views.calendar, name='calendar'),
    path('booking', views.new_booking, name='booking'),
    path('booking/<int:id>/', views.booking, name='booking'),
    path('markdownx/', include(markdownx)),
]

if not settings.DEBUG:
    urlpatterns += [re_path(r'^media/(?P<path>.*)', views.media, name='media')]
