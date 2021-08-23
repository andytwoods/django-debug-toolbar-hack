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


def load_view(request):
    match = resolve(request.path)
    func, args, kwargs = match
    info = inspect.getsourcefile(func)
    el = load_element(info)
    print(1)
    return el

def load_template(request):
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

    final_loaders = []
    loaders = Engine.get_default().template_loaders

    for loader in loaders:
        if loader is not None:
            # When the loader has loaders associated with it,
            # append those loaders to the list. This occurs with
            # django.template.loaders.cached.Loader
            if hasattr(loader, "loaders"):
                final_loaders += loader.loaders
            else:
                final_loaders.append(loader)

    open_backend = request.GET.get('open_backend', True)

    if open_backend:
        origin = str(Origin(template_origin_name))
        return load_element(origin)

def load_element(el):
    """
    Return the source of a template, syntax-highlighted by Pygments if
    it's available.
    """

    try:
        ide = settings.DJANGO_IDE
    except AttributeError:
        ide = 'C:/Program Files/JetBrains/PyCharm 2020.1/bin/pycharm64.exe'

    if sys.platform == 'win32':
        print(el)

        p = subprocess.Popen([ide, el])

    elif sys.platform == 'darwin':
        subprocess.Popen(['open', el])

    else:
        try:
            subprocess.Popen(['xdg-open', el])
        except OSError:
            pass
    return JsonResponse({})

