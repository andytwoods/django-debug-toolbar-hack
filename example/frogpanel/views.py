import inspect
import subprocess
import sys

from django.conf import settings
from django.http import JsonResponse
from django.template.loader import get_template
from django.urls import resolve


def _retrieve_template_name(request):
    template_name = request.GET.get('template')
    template = get_template(template_name)
    return template.origin.name

def open_template(request):
    template_name = _retrieve_template_name(request)
    return open_element(template_name)

def _retrieve_view_name(request):
    host = request.get_host()
    referrer = request.META['HTTP_REFERER']
    url_ending = referrer.split(host)[1]
    match = resolve(url_ending)
    func, _, _ = match
    return inspect.getsourcefile(func)


def open_view(request):
    view_name = _retrieve_view_name(request)
    return open_element(view_name)


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

