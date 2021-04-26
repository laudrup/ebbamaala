from unittest import mock
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from website.models import PracticalInfo


class PracticalInfoViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('bobby', 'littlebobby@gmail.com', 'tables')

    def test_not_logged_in(self):
        response = self.client.get('/info')
        url = "{}?{}".format(settings.LOGIN_URL, urlencode({'next': '/info'}))
        self.assertRedirects(response, url)

    @mock.patch('website.views.logger')
    def test_no_info(self, mock_logger):
        self.client.login(username='bobby', password='tables')

        response = self.client.get('/info')
        self.assertEqual(404, response.status_code)
        mock_logger.warning.assert_called_with('No practical info added')

    def test_practical_info_added(self):
        practical_info_content = b'The moose is on the loose'
        PracticalInfo.objects.create(content=practical_info_content)
        self.client.login(username='bobby', password='tables')

        response = self.client.get('/info')
        self.assertEqual(200, response.status_code)
        self.assertIn(practical_info_content, response.content)
