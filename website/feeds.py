from django_ical.views import ICalFeed
from .models import Booking


class BookingFeed(ICalFeed):
    product_id = '-//ebbamåla.se//Bookings//EN'
    timezone = 'UTC'
    file_name = 'bookings.ics'
    title = 'Ebbamåla'

    def items(self):
        return Booking.objects.all().order_by('-start_date')

    def item_title(self, item):
        return str(item)

    def item_description(self, item):
        return item.description

    def item_start_datetime(self, item):
        return item.start_date

    def item_end_datetime(self, item):
        return item.end_date

    def item_geolocation(self, item):
        return (56.500111, 15.471333)

    def item_guid(self, item):
        return f'{item.start_date}-{item.end_date}-{item.pk}@ebbamåla.se'
