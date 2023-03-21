import base64
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse
from django.test import RequestFactory, TestCase

from website.middleware import LoginRequiredMiddleware


class LoginRequiredMiddlewareTests(TestCase):
    def setUp(self):
        self.middleware = LoginRequiredMiddleware(self.get_response)
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user('bobby', 'littlebobby@gmail.com', 'tables')

    def get_response(self, request):
        return HttpResponse()

    def test_no_redirect_login_url(self):
        request = self.factory.get(settings.LOGIN_URL)
        request.user = AnonymousUser()
        response = self.middleware(request)
        self.assertEqual(200, response.status_code)

    def test_no_content_header(self):
        request = self.factory.get('/')
        request.user = AnonymousUser()
        response = self.middleware(request)
        url = "{}?{}".format(settings.LOGIN_URL, urlencode({'next': '/'}))
        self.assertRedirects(response, url, fetch_redirect_response=False)

    def test_redirect_html_accept_header(self):
        request = self.factory.get('/', {}, HTTP_ACCEPT='text/html')
        request.user = AnonymousUser()
        response = self.middleware(request)
        url = "{}?{}".format(settings.LOGIN_URL, urlencode({'next': '/'}))
        self.assertRedirects(response, url, fetch_redirect_response=False)

    def test_no_redirect_json_accept_header(self):
        request = self.factory.get('/', {}, HTTP_ACCEPT='application/json')
        request.user = AnonymousUser()
        response = self.middleware(request)
        self.assertEqual(401, response.status_code)

    def test_valid_basic_auth(self):
        b64auth = base64.b64encode(b'bobby:tables').decode('utf-8')
        request = self.factory.get('/', {}, HTTP_AUTHORIZATION=f'Basic {b64auth}')
        request.user = AnonymousUser()
        response = self.middleware(request)
        self.assertEqual(200, response.status_code)
        self.assertEqual(self.user, request.user)

    def test_invalid_basic_auth_credentials(self):
        b64auth = base64.b64encode(b'evil:hacker').decode('utf-8')
        request = self.factory.get('/', {}, HTTP_AUTHORIZATION=f'Basic {b64auth}', HTTP_ACCEPT='application/json')
        request.user = AnonymousUser()
        response = self.middleware(request)
        self.assertEqual(401, response.status_code)

    def test_invalid_basic_auth(self):
        request = self.factory.get('/', {}, HTTP_AUTHORIZATION='Basic notbase64', HTTP_ACCEPT='application/json')
        request.user = AnonymousUser()
        response = self.middleware(request)
        self.assertEqual(401, response.status_code)
