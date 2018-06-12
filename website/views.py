from django.shortcuts import render


def index(request):
    return render(request, 'website/index.html', {})


def info(request):
    return render(request, 'website/info.html', {})
