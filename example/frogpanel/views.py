import inspect
import pathlib
import subprocess
import subprocess
import sys
from django.conf import settings
from django.core import signing
from django.http import HttpResponseBadRequest, JsonResponse
from django.template import Origin, TemplateDoesNotExist
from django.template.engine import Engine
from django.template.loader import render_to_string
from django.urls import resolve
from django.utils.safestring import mark_safe

from debug_toolbar.decorators import require_show_toolbar
from debug_toolbar.utils import get_name_from_obj


def open_view(request):
    # stolen from debug_toolbar\panels\templates\views.py
    """
    Return the source of a template, syntax-highlighted by Pygments if
    it's available.
    """

    template_origin_name = request.GET.get("template_origin")
    if template_origin_name is None:
        return HttpResponseBadRequest('"template_origin" key is required')
    try:
        template_origin_name = signing.loads(template_origin_name)
    except Exception:
        return HttpResponseBadRequest('"template_origin" is invalid')
    template_name = request.GET.get("template", template_origin_name)

    origin = str(Origin(template_origin_name))
    return open_element(origin)


def open_template(request):
    match = resolve(request.path)
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

