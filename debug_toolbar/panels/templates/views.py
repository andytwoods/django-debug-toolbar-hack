import subprocess
import subprocess
import sys

from django.core import signing
from django.http import HttpResponseBadRequest, JsonResponse
from django.template import Origin, TemplateDoesNotExist
from django.template.engine import Engine
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from debug_toolbar.decorators import require_show_toolbar


@require_show_toolbar
def template_source(request):
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
        if sys.platform == 'win32':
            print(origin)
            p = subprocess.Popen(["C:/Program Files/JetBrains/PyCharm 2020.1/bin/pycharm64.exe", origin])

        elif sys.platform == 'darwin':
            subprocess.Popen(['open', origin])

        else:
            try:
                subprocess.Popen(['xdg-open', origin])
            except OSError:
                pass
        return JsonResponse({})

    for loader in final_loaders:
        origin = Origin(template_origin_name)
        try:
            source = loader.get_contents(origin)
            break
        except TemplateDoesNotExist:
            pass
    else:
        source = "Template Does Not Exist: {}".format(template_origin_name)

    try:
        from pygments import highlight
        from pygments.formatters import HtmlFormatter
        from pygments.lexers import HtmlDjangoLexer

        source = highlight(source, HtmlDjangoLexer(), HtmlFormatter())
        source = mark_safe(source)
        source.pygmentized = True
    except ImportError:
        pass

    content = render_to_string(
        "debug_toolbar/panels/template_source.html",
        {"source": source, "template_name": template_name},
    )
    return JsonResponse({"content": content})
