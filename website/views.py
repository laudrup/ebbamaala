import calendar as cal
import datetime
import logging

from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils.translation import gettext_noop
from django_weasyprint.views import WeasyTemplateView

from .forms import BookingForm
from .models import Booking, Frontpage, Gallery, Trips

logger = logging.getLogger(__name__)


INFO_SECTIONS = {
    'travel_guide': {
        'title': gettext_noop('Travel Guide'),
        'orientation': 'portrait',
    },
    'waste_sorting': {
        'title': gettext_noop('Waste Sorting'),
        'orientation': 'landscape',
    },
    'wilderness_bath': {
        'title': gettext_noop('Wilderness Bath'),
        'orientation': 'portrait',
    },
}


def index(request):
    try:
        frontpage = Frontpage.objects.latest('pub_date')
    except Frontpage.DoesNotExist:
        logger.warning('No frontpage added')
        raise Http404
    return render(request, 'website/index.html', {'frontpage': frontpage})


def info(request):
    return render(request, 'website/info.html', {'sections': INFO_SECTIONS})


def trips(request):
    try:
        trips = Trips.objects.latest('pub_date')
    except Trips.DoesNotExist:
        logger.warning('No trips added')
        raise Http404
    return render(request, 'website/trips.html', {'trips': trips})


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
    booking = get_object_or_404(Booking, pk=id)

    if request.method == 'POST':
        if 'update' in request.POST:
            if not request.user.is_superuser and request.user != booking.user:
                raise PermissionDenied
            instance = get_object_or_404(Booking, id=id)
            form = BookingForm(request.user, request.POST, instance=instance)
            if form.is_valid():
                form.save()
            else:
                return render(request, 'website/edit_booking.html', {'booking': booking, 'form': form})
        elif 'delete' in request.POST:
            if not request.user.is_superuser and request.user != booking.user:
                raise PermissionDenied
            booking.delete()
        elif 'approve' in request.POST:
            if not request.user.is_superuser:
                raise PermissionDenied
            booking.approved = True
            booking.save()
        else:
            raise SuspiciousOperation
        return HttpResponseRedirect(reverse('website:calendar'))

    if request.user.is_superuser or request.user == booking.user:
        form = BookingForm(request.user,
                           initial={'start_date': booking.start_date,
                                    'end_date': booking.end_date,
                                    'booker': booking.booker,
                                    'description': booking.description})
        return render(request, 'website/edit_booking.html', {'booking': booking, 'form': form})

    return render(request, 'website/booking.html', {'booking': booking})


def new_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('website:calendar'))
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

    return render(request, 'website/edit_booking.html', {'form': form})


def media(request, path):
    response = HttpResponse()
    del response['Content-Type']
    response['X-Accel-Redirect'] = '/protected/media/{}'.format(path).encode('utf-8')
    return response


class PdfView(WeasyTemplateView):
    logging.getLogger('fontTools').setLevel(logging.ERROR)
    logging.getLogger('weasyprint').setLevel(logging.ERROR)
    logging.getLogger('django_weasyprint').setLevel(logging.ERROR)
    logging.getLogger('PIL').setLevel(logging.ERROR)

    template_name = 'website/pdf_base.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        name = context['name']
        if name not in INFO_SECTIONS:
            raise Http404
        context.update(INFO_SECTIONS[name])
        return context
