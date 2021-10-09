import inspect
import subprocess
import sys

from django.conf import settings
from django.core import signing
from django.http import HttpResponseBadRequest, JsonResponse
from django.template import Origin
from django.urls import resolve, reverse


def open_template(request):

    # stolen from debug_toolbar\panels\templates\views.py
    """
    Return the source of a template, syntax-highlighted by Pygments if
    it's available.
    """

    urls = {
        'ABSOLUTE_ROOT': request.build_absolute_uri('/')[:-1].strip("/"),
        'ABSOLUTE_ROOT_URL': request.build_absolute_uri('/').strip("/"),
    }
    host = request.get_host()
    url_name = resolve(request.path_info).url_name
    referrer = request.META['HTTP_REFERER']

    url_ending = referrer.split(host)[1].lstrip("/")
    named_url = reverse(request.path_info)
    print(named_url)
    return ''

    origin = str(Origin(template_origin_name))
    return open_element(origin)


def open_view(request):

    host = request.get_host()
    referrer = request.META['HTTP_REFERER']

    url_ending = referrer.split(host)[1]

    match = resolve(url_ending)
    func, _, _ = match
    info = inspect.getsourcefile(func)
    return open_element(info)


def open_element(el):
    """
    Return the source of a template, syntax-highlighted by Pygments if
    it's available.
    """

    try:
        ide = settings.DJANGO_IDE
    except AttributeError:
        ide = 'open'

    if sys.platform == 'win32':
        subprocess.Popen([ide, el])

    elif sys.platform == 'darwin':
        subprocess.Popen(['open', el])

    else:
        try:
            subprocess.Popen(['xdg-open', el])
        except OSError:
            pass
    return JsonResponse({})

