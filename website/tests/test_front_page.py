from urllib.parse import urlencode

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from website.models import Frontpage


class FrontpageViewTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user('bobby', 'littlebobby@gmail.com', 'tables')

    def test_not_logged_in(self):
        response = self.client.get('/')
        url = "{}?{}".format(settings.LOGIN_URL, urlencode({'next': '/'}))
        self.assertRedirects(response, url)

    def test_no_frontage(self):
        self.client.login(username='bobby', password='tables')

        response = self.client.get('/')
        self.assertEqual(404, response.status_code)

    def test_frontpage_added(self):
        frontpage_header = 'Welcome to the frontpage'
        frontpage_content = 'Here is a lot of interesting information'
        Frontpage.objects.create(content='#{header}\n{content}'.format(header=frontpage_header,
                                                                       content=frontpage_content))
        self.client.login(username='bobby', password='tables')

        response = self.client.get('/')
        self.assertEqual(200, response.status_code)

        # The markdown formatted text should be converted to HTML
        soup = BeautifulSoup(response.content, 'lxml')
        main_elements = soup.find_all('main')
        self.assertEqual(1, len(main_elements))

        main = main_elements[0]
        header = main.h1
        self.assertIsNotNone(header)
        self.assertEqual(1, len(header.contents))
        self.assertEqual(frontpage_header, header.contents[0])

        content = main.p
        self.assertIsNotNone(content)
        self.assertEqual(1, len(content.contents))
        self.assertEqual(frontpage_content, content.contents[0])

        new_frontpage_header = 'New frontpage'
        new_frontpage_content = 'With new information'
        Frontpage.objects.create(content='#{header}\n{content}'.format(header=new_frontpage_header,
                                                                       content=new_frontpage_content))

        response = self.client.get('/')
        self.assertEqual(200, response.status_code)

        # The markdown formatted text should be converted to HTML
        soup = BeautifulSoup(response.content, 'lxml')
        main_elements = soup.find_all('main')
        self.assertEqual(1, len(main_elements))

        main = main_elements[0]
        header = main.h1
        self.assertIsNotNone(header)
        self.assertEqual(1, len(header.contents))
        self.assertEqual(new_frontpage_header, header.contents[0])

        content = main.p
        self.assertIsNotNone(content)
        self.assertEqual(1, len(content.contents))
        self.assertEqual(new_frontpage_content, content.contents[0])
