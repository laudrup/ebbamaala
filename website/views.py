from django.http import HttpResponse
from django.shortcuts import render

from .models import Frontpage, PracticalInfo


def index(request):
    frontpage = Frontpage.objects.latest('pub_date')
    return render(request, 'website/index.html', {'frontpage': frontpage})


def info(request):
    info = PracticalInfo.objects.latest('pub_date')
    return render(request, 'website/info.html', {'info': info})


def media(request, path):
    response = HttpResponse()
    del response['Content-Type']
    response['X-Accel-Redirect'] = '/protected/media/{}'.format(path)
    return response
