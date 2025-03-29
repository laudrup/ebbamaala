import base64
from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from ics import Calendar, geo

from website.models import Booking


class calendarFeedTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user('bobby', 'littlebobby@gmail.com', 'tables')

    def test_not_authenticated(self):
        response = self.client.get('/bookings.ics', {}, HTTP_ACCEPT='text/calendar')
        self.assertEqual(401, response.status_code)

    def test_empty_calendar(self):
        b64auth = base64.b64encode(b'bobby:tables').decode('utf-8')
        response = self.client.get('/bookings.ics', {}, HTTP_AUTHORIZATION=f'Basic {b64auth}')
        self.assertEqual(200, response.status_code)
        calendar = Calendar(response.content.decode('utf-8'))
        self.assertFalse(calendar.events)

    def test_calendar_entry(self):
        start_date = date(2023, 7, 20)
        end_date = date(2023, 7, 26)
        booker = 'Bamse'
        description = 'Hyggetur med kylling'
        booking = Booking.objects.create(start_date=start_date,
                                         end_date=end_date,
                                         user=self.user,
                                         booker=booker,
                                         description=description)
        self.assertEqual(1, len(Booking.objects.all()))

        b64auth = base64.b64encode(b'bobby:tables').decode('utf-8')
        response = self.client.get('/bookings.ics', {}, HTTP_AUTHORIZATION=f'Basic {b64auth}')
        self.assertEqual(200, response.status_code)
        calendar = Calendar(response.content.decode('utf-8'))

        self.assertEqual(1, len(calendar.events))
        event = calendar.events.pop()
        self.assertEqual(f'{booker}s booking', event.summary)
        self.assertEqual(start_date, event.begin.date())
        self.assertEqual(end_date, event.end.date())
        self.assertEqual(event.description, description)
        self.assertEqual(response.wsgi_request.build_absolute_uri(booking.get_absolute_url()), event.url)
        self.assertEqual(geo.Geo(latitude=56.500111, longitude=15.471333), event.geo)
