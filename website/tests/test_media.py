from urllib.parse import urlencode

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.conf import settings


class MediaViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('bobby', 'littlebobby@gmail.com', 'tables')

    def test_not_logged_in(self):
        response = self.client.get('/media/some_image.png')
        url = "{}?{}".format(settings.LOGIN_URL, urlencode({'next': '/media/some_image.png'}))
        self.assertRedirects(response, url)

    def test_redirect_set(self):
        self.client.login(username='bobby', password='tables')
        response = self.client.get('/media/some_image.png')
        self.assertEqual(200, response.status_code)
        self.assertIn('X-Accel-Redirect', response)
        self.assertEqual('/protected/media/some_image.png', response['X-Accel-Redirect'])
        self.assertNotIn('Content-Type', response)
