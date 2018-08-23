from datetime import date

from bs4 import BeautifulSoup
from django.contrib.auth import get_user_model
from django.test import TestCase
from website.forms import BookingForm
from website.models import Booking


class BookingFormTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self._user = User.objects.create_user('bobby', 'littlebobby@gmail.com', 'tables')

    def test_valid_booking(self):
        form = self._booking_form(date(2018, 7, 25), date(2018, 7, 27))

        self.assertTrue(form.is_valid())
        self.assertEqual(0, len(form.errors))
        form.save()
        self.assertEqual(1, len(Booking.objects.all()))

    def test_missing_dates(self):
        form = self._booking_form(None, None)
        self.assertFalse(form.is_valid())

    def test_end_before_start(self):
        form = self._booking_form(date(2018, 7, 27), date(2018, 7, 25))
        self.assertFalse(form.is_valid())
        self.assertEqual(1, len(form.errors))
        self.assertIn('Booking cannot end before it starts.', str(form.errors))

    def test_overlapping_booking(self):
        form = self._booking_form(date(2018, 7, 25), date(2018, 7, 27))
        form.save()

        for dates in ((date(2018, 7, 20), date(2018, 7, 26)),
                      (date(2018, 7, 26), date(2018, 7, 30)),
                      (date(2018, 7, 20), date(2018, 7, 30))):
            form = self._booking_form(dates[0], dates[1])
            self.assertFalse(form.is_valid())
            self.assertIn('bobby has already booked these dates.', str(form.errors))

        form = self._booking_form(date(2018, 7, 28), date(2018, 7, 30))
        self.assertTrue(form.is_valid())

        form = self._booking_form(date(2018, 7, 22), date(2018, 7, 24))
        self.assertTrue(form.is_valid())

    def _booking_form(self, start_date, end_date):
        return BookingForm(self._user,
                           {'description': 'Not important',
                            'start_date': start_date,
                            'end_date': end_date})


class BookingViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        User.objects.create_user('alice', 'bob@nowhere.invalid', 'password')
        User.objects.create_user('bob', 'alice@nowhere.invalid', 'password')
        User.objects.create_user('admin', 'admin@nowhere.invalid', 'password', is_superuser=True)

    def test_delete_booking(self):
        self.client.login(username='alice', password='password')
        response = self.client.post('/booking', {'description': 'Not important',
                                                 'start_date': date(2018, 7, 25),
                                                 'end_date': date(2018, 7, 27)})
        self.assertEqual(1, len(Booking.objects.all()))
        alice_booking_url = response.url

        # Alice should have a form for deleting her booking
        soup = BeautifulSoup(self.client.get(alice_booking_url).content, 'lxml')
        self.assertIsNotNone(soup.find(id='delete_booking'))

        # Bob should not have a form for deleting Alices booking
        self.client.login(username='bob', password='password')
        soup = BeautifulSoup(self.client.get(alice_booking_url).content, 'lxml')
        self.assertIsNone(soup.find(id='delete_booking'))

        # Bob cannot delete Alices booking
        response = self.client.post(alice_booking_url, {'type': 'delete'})
        self.assertEqual(403, response.status_code)
        self.assertEqual(1, len(Booking.objects.all()))

        # Bob can create his own booking and delete that
        response = self.client.post('/booking', {'description': 'Not important',
                                                 'start_date': date(2018, 7, 28),
                                                 'end_date': date(2018, 7, 30)})
        self.assertEqual(2, len(Booking.objects.all()))
        bob_booking_url = response.url
        response = self.client.post(bob_booking_url, {'type': 'delete'})
        self.assertNotEqual(403, response.status_code)
        self.assertEqual(1, len(Booking.objects.all()))

        # Admin should have a form for deleting Alices booking
        self.client.login(username='admin', password='password')
        soup = BeautifulSoup(self.client.get(alice_booking_url).content, 'lxml')
        self.assertIsNotNone(soup.find(id='delete_booking'))

        # Admin can delete all bookings
        response = self.client.post(alice_booking_url, {'type': 'delete'})
        self.assertNotEqual(403, response.status_code)
        self.assertEqual(0, len(Booking.objects.all()))


    def test_approve_booking(self):
        self.client.login(username='alice', password='password')
        response = self.client.post('/booking', {'description': 'Not important',
                                                 'start_date': date(2018, 7, 25),
                                                 'end_date': date(2018, 7, 27)})
        self.assertEqual(1, len(Booking.objects.all()))
        booking = Booking.objects.all().last()
        self.assertFalse(booking.approved)

        # Alice cannot approve her own booking
        alice_booking_url = response.url
        response = self.client.post(alice_booking_url, {'type': 'approve'})
        self.assertEqual(403, response.status_code)
        self.assertFalse(Booking.objects.all().last().approved)

        # And neither can Bob
        self.client.login(username='bob', password='password')
        response = self.client.post(alice_booking_url, {'type': 'approve'})
        self.assertEqual(403, response.status_code)
        self.assertFalse(Booking.objects.all().last().approved)

        # But an admin can
        self.client.login(username='admin', password='password')
        response = self.client.post(alice_booking_url, {'type': 'approve'})
        self.assertEqual(302, response.status_code)
        self.assertTrue(Booking.objects.all().last().approved)

    def test_admin_booking_approved(self):
        # An admin doesn't have to approve her own booking
        self.client.login(username='admin', password='password')
        response = self.client.post('/booking', {'description': 'Not important',
                                                 'start_date': date(2018, 7, 25),
                                                 'end_date': date(2018, 7, 27)})
        self.assertEqual(1, len(Booking.objects.all()))
        booking = Booking.objects.all().last()
        self.assertTrue(booking.approved)
