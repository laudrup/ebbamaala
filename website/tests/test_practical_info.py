from os.path import basename, splitext
from urllib.parse import urlencode

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from website.views import InfoView


class PracticalInfoViewTests(TestCase):

    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('bobby', 'littlebobby@gmail.com',
                                             'tables')

    def test_not_logged_in(self):
        response = self.client.get('/info')
        url = "{}?{}".format(settings.LOGIN_URL, urlencode({'next': '/info'}))
        self.assertRedirects(response, url)

    def test_practical_info_content(self):
        self.client.login(username='bobby', password='tables')

        response = self.client.get('/info')
        self.assertEqual(200, response.status_code)
        soup = BeautifulSoup(response.content, 'lxml')

        headers = [(h.contents[0].strip(), h.find('a')['href'])
                   for h in soup.find_all('h1') if h.find('a', href=True)]
        for h in headers:
            name = splitext(basename(h[1]))[0]
            if name == 'practical_info':
                continue
            self.assertIn(name, InfoView.sections)
            self.assertEqual(h[0], InfoView.sections[name]['title'])

        for name in InfoView.sections:
            self.assertIn(InfoView.sections[name]['title'],
                          [h[0] for h in headers])
