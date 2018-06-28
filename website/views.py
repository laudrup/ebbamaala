import os

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render

from .models import Frontpage


def index(request):
    frontpage = Frontpage.objects.latest('pub_date')
    return render(request, 'website/index.html', {'frontpage': frontpage})


def info(request):
    return render(request, 'website/info.html', {})


def media(request, filename):
    response = HttpResponse()
    response['Content-Type'] = ''
    response['X-Sendfile'] = (os.path.join(settings.MEDIA_ROOT, filename))
    return response
