import base64

from django.conf import settings
from django.contrib.auth import authenticate
from django.http import HttpResponse, HttpResponseRedirect


def validate_basic_auth(request):
    if 'HTTP_AUTHORIZATION' in request.META:
        auth = request.META['HTTP_AUTHORIZATION'].split()
        if len(auth) == 2 and auth[0].lower() == 'basic':
            try:
                decoded_header = base64.b64decode(auth[1]).decode('utf-8')
            except base64.binascii.Error:
                return False
            uname, passwd = decoded_header.split(':')
            user = authenticate(username=uname, password=passwd)
            if user is not None and user.is_active:
                request.user = user
                return True
    return False


class LoginRequiredMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated and not validate_basic_auth(request):
            if ('HTTP_ACCEPT' in request.META and 'text/html'
                    not in request.META['HTTP_ACCEPT'].split(',')):
                return HttpResponse(status=401)
            if not request.path_info == settings.LOGIN_URL:
                params = request.GET.copy()
                params['next'] = request.path
                url = "{}?{}".format(settings.LOGIN_URL, params.urlencode())
                return HttpResponseRedirect(url)

        response = self.get_response(request)
        return response
