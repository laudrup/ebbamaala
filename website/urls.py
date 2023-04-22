from markdownx import urls as markdownx
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls import static

from . import views
from .feeds import BookingFeed


app_name = 'website'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('info', views.InfoView.as_view(), name='info'),
    path('trips', views.TripsView.as_view(), name='trips'),
    path('gallery', views.GalleryView.as_view(), name='gallery'),
    path('gallery/<gallery_id>/', views.GalleryView.as_view(), name='photos'),
    path('calendar', views.CalendarView.as_view(), name='calendar'),
    path('calendar/<int:year>/<int:month>/', views.CalendarView.as_view(), name='calendar'),
    path('booking', views.BookingView.as_view(), name='booking'),
    path('booking/<int:id>/', views.BookingView.as_view(), name='booking'),
    path('markdownx/', include(markdownx)),
    path('bookings.ics', BookingFeed(), name='feeds'),
    path('<str:name>.pdf', views.PdfView.as_view(), name='pdf'),
]

if settings.DEBUG:
    urlpatterns += static.static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [re_path(r'^media/(?P<path>.*)', views.MediaView.as_view(), name='media')]
