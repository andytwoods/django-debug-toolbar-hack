import inspect
import subprocess
import sys

from django.conf import settings
from django.http import JsonResponse
from django.template.loader import get_template
from django.urls import resolve


def open_template(request):
    template_name = request.GET.get('template')
    template = get_template(template_name)
    return open_element(template.origin.name)


def open_view(request):
    host = request.get_host()
    referrer = request.META['HTTP_REFERER']
    url_ending = referrer.split(host)[1]

    match = resolve(url_ending)
    func, _, _ = match
    info = inspect.getsourcefile(func)
    return open_element(info)


def open_element(el):

    if sys.platform == 'win32':
        try:
            ide = settings.DJANGO_WINDOWS_IDE
        except AttributeError:
            ide = 'open'
        subprocess.Popen([ide, el])

    elif sys.platform == 'darwin':
        subprocess.call(('open', el))

    else:
        try:
            subprocess.Popen(['xdg-open', el])
        except OSError:
            pass
    return JsonResponse({})

