import subprocess
import sys
import webbrowser

from django.http import Http404, JsonResponse
from django.urls import resolve, path, reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from debug_toolbar.panels import Panel
from debug_toolbar.utils import get_name_from_obj, get_sorted_request_variable


class RequestPanel(Panel):
    """
    A panel to display request variables (POST/GET, session, cookies).
    """

    template = "debug_toolbar/panels/request.html"

    title = _("Request")

    @classmethod
    def get_urls(cls):
        return [path("py_source/", cls.py_source, name="py_source")]

    @classmethod
    def py_source(requestpanel, request):

        match = resolve(request.path)
        func, args, kwargs = match
        print(get_name_from_obj(func),33)

        origin = '/Users/andytwoods/PycharmProjects/django-debug-toolbar/debug_toolbar/panels/redirects.py'
        webbrowser.open(origin)
        if sys.platform == 'win32':
            subprocess.Popen(['start', origin], shell=True)

        elif sys.platform == 'darwin':
            subprocess.Popen(['open', origin])

        else:
            try:
                subprocess.Popen(['xdg-open', origin])
            except OSError:
                pass
        return JsonResponse({})

    @property
    def nav_subtitle(self):
        """
        Show abbreviated name of view function as subtitle
        """
        view_func = self.get_stats().get("view_func", "")

        view_name =  view_func.rsplit(".", 1)[-1]
        return mark_safe(f"<a class='djdt-backend-open' href='{reverse('djdt:py_source')}'>{view_name}</a>")

    def generate_stats(self, request, response):
        self.record_stats(
            {
                "get": get_sorted_request_variable(request.GET),
                "post": get_sorted_request_variable(request.POST),
                "cookies": get_sorted_request_variable(request.COOKIES),
            }
        )

        view_info = {
            "view_func": _("<no view>"),
            "view_args": "None",
            "view_kwargs": "None",
            "view_urlname": "None",
        }
        try:
            match = resolve(request.path)
            func, args, kwargs = match
            link = mark_safe(f"<a class='djdt-backend-open' href='{reverse('djdt:py_source')}'>"
                             f"{get_name_from_obj(func)}</a>")
            view_info["view_func"] = link
            view_info["view_args"] = args
            view_info["view_kwargs"] = kwargs

            if getattr(match, "url_name", False):
                url_name = match.url_name
                if match.namespaces:
                    url_name = ":".join([*match.namespaces, url_name])
            else:
                url_name = _("<unavailable>")

            view_info["view_urlname"] = url_name

        except Http404:
            pass
        self.record_stats(view_info)

        if hasattr(request, "session"):
            self.record_stats(
                {
                    "session": [
                        (k, request.session.get(k))
                        for k in sorted(request.session.keys())
                    ]
                }
            )
