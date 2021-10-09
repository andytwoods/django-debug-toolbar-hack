import inspect
import subprocess
import sys

from django.conf import settings
from django.core import signing
from django.http import HttpResponseBadRequest, JsonResponse
from django.template import Origin, Engine, TemplateDoesNotExist
from django.template.loader import render_to_string, get_template
from django.urls import resolve, reverse


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

