from django.test import TestCase
from django.contrib.auth import get_user_model

from datetime import date

from website.forms import BookingForm
from website.models import Booking


class BookingFormTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('bobby', 'littlebobby@gmail.com', 'tables')
        # self.client.login(username='bobby', password='tables')

    def test_valid_booking(self):
        form = self._booking_form(date(2018, 7, 25), date(2018, 7, 27))

        self.assertTrue(form.is_valid())
        self.assertEqual(0, len(form.errors))
        form.save()
        self.assertEqual(1, len(Booking.objects.all()))

    def test_end_before_start(self):
        form = self._booking_form(date(2018, 7, 27), date(2018, 7, 25))
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertIn('Booking cannot end before it starts.', str(form.errors))

    def test_overlapping_booking(self):
        form = self._booking_form(date(2018, 7, 25), date(2018, 7, 27))
        form.save()

        form = self._booking_form(date(2018, 7, 20), date(2018, 7, 26))
        self.assertFalse(form.is_valid())
        self.assertIn('bobby has already booked these dates.', str(form.errors))

        form = self._booking_form(date(2018, 7, 26), date(2018, 7, 30))
        self.assertFalse(form.is_valid())
        self.assertIn('bobby has already booked these dates.', str(form.errors))

        form = self._booking_form(date(2018, 7, 20), date(2018, 7, 30))
        self.assertFalse(form.is_valid())
        self.assertIn('bobby has already booked these dates.', str(form.errors))

        form = self._booking_form(date(2018, 7, 28), date(2018, 7, 30))
        self.assertTrue(form.is_valid())

        form = self._booking_form(date(2018, 7, 22), date(2018, 7, 24))
        self.assertTrue(form.is_valid())

    def _booking_form(self, start_date, end_date):
        return BookingForm(self.user,
                           {'description': 'Not important',
                            'start_date': start_date,
                            'end_date': end_date})
