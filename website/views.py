import calendar as cal
import datetime

from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .forms import BookingForm
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
    bookings = Booking.objects.filter(start_date__lte=end_date, end_date__gte=start_date)
    next_month = (year, month + 1) if month < 12 else (year + 1, 1)
    prev_month = (year, month - 1) if month > 1 else (year - 1, 12)
    return render(request, 'website/calendar.html', {'year': year,
                                                     'month': month,
                                                     'next_month': next_month,
                                                     'prev_month': prev_month,
                                                     'bookings': bookings})


def booking(request, id):
    if request.method == 'POST':
        # TODO: Delete booking
        pass
    booking = get_object_or_404(Booking, pk=id)
    return render(request, 'website/booking.html', {'booking': booking})


def new_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.user, request.POST)
        if form.is_valid():
            saved_form = form.save()
            return HttpResponseRedirect(reverse('website:booking', args=(saved_form.id, )))
    else:
        if all(val in request.GET for val in ['year', 'month', 'day']):
            start_date = datetime.date(int(request.GET['year']),
                                       int(request.GET['month']),
                                       int(request.GET['day']))
        else:
            start_date = datetime.date.today()

        form = BookingForm(request.user,
                           initial={'start_date': start_date,
                                    'end_date': start_date + datetime.timedelta(days=2)})

    return render(request, 'website/new_booking.html', {'form': form})


def media(request, path):
    response = HttpResponse()
    del response['Content-Type']
    response['X-Accel-Redirect'] = '/protected/media/{}'.format(path)
    return response
