import calendar as cal
import datetime

from django.http import Http404, HttpResponse
from django.shortcuts import render

from .models import Booking, Frontpage, Gallery, PracticalInfo


def index(request):
    frontpage = Frontpage.objects.latest('pub_date')
    return render(request, 'website/index.html', {'frontpage': frontpage})


def info(request):
    info = PracticalInfo.objects.latest('pub_date')
    return render(request, 'website/info.html', {'info': info})


def gallery(request):
    galleries = Gallery.objects.all()
    return render(request, 'website/gallery.html', {'galleries': galleries})


def photos(request, gallery_id):
    gallery = Gallery.objects.get(slug=gallery_id)
    return render(request, 'website/photos.html', {'gallery': gallery})


def calendar(request, year=None, month=None):
    now = datetime.datetime.now()
    if not year:
        year = now.year
    if not month:
        month = now.month
    if month > 12:
        raise Http404()

    last_day = cal.monthrange(year, month)[1]
    start_date = datetime.date(year, month, 1)
    end_date = datetime.date(year, month, last_day)
    bookings = Booking.objects.filter(start__lte=end_date, end__gte=start_date)
    if bookings:
        print('We have bookings in {}'.format(month))
    # print('Last day is: {}'.format(last_day))
    next_month = (year, month + 1) if month < 12 else (year + 1, 1)
    prev_month = (year, month - 1) if month > 1 else (year - 1, 12)
    return render(request, 'website/calendar.html', {'year': year,
                                                     'month': month,
                                                     'next_month': next_month,
                                                     'prev_month': prev_month,
                                                     'bookings': bookings})


def media(request, path):
    response = HttpResponse()
    del response['Content-Type']
    response['X-Accel-Redirect'] = '/protected/media/{}'.format(path)
    return response
