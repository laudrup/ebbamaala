from django.http import HttpResponseRedirect
from django.conf import settings


class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            if not request.path_info == settings.LOGIN_URL:
                params = request.GET.copy()
                params['next'] = request.path
                url = "{}?{}".format(settings.LOGIN_URL, params.urlencode())
                return HttpResponseRedirect(url)

        response = self.get_response(request)
        return response
