from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from website.models import Trips


class TripsViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('bobby', 'littlebobby@gmail.com', 'tables')

    def test_not_logged_in(self):
        response = self.client.get('/trips')
        url = "{}?{}".format(settings.LOGIN_URL, urlencode({'next': '/trips'}))
        self.assertRedirects(response, url)

    def test_no_trips(self):
        self.client.login(username='bobby', password='tables')

        response = self.client.get('/trips')
        self.assertEqual(404, response.status_code)

    def test_trips_added(self):
        trips_content = b'Go spot a moose'
        Trips.objects.create(content=trips_content)
        self.client.login(username='bobby', password='tables')

        response = self.client.get('/trips')
        self.assertEqual(200, response.status_code)
        self.assertIn(trips_content, response.content)
