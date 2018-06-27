from django.shortcuts import render

from .models import Frontpage


def index(request):
    frontpage = Frontpage.objects.latest('pub_date')
    return render(request, 'website/index.html', {'frontpage': frontpage})


def info(request):
    return render(request, 'website/info.html', {})
