from collections import OrderedDict
from contextlib import contextmanager
from os.path import normpath
from pprint import pformat, saferepr

from django import http
from django.core import signing
from django.db.models.query import QuerySet, RawQuerySet
from django.template import RequestContext, Template, loader
from django.test.signals import template_rendered
from django.test.utils import instrumented_test_render
from django.urls import path, resolve
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from debug_toolbar.panels import Panel
from debug_toolbar.panels.sql.tracking import SQLQueryTriggered, recording
# Code taken and adapted from Simon Willison and Django Snippets:
# https://www.djangosnippets.org/snippets/766/
from debug_toolbar.utils import get_name_from_obj
from example.frogpanel import views

class FrogPanel(Panel):
    """
    A panel that lists all templates used during processing of a response.
    """


    def _store_template_info(self, sender, **kwargs):
        template, context = kwargs["template"], kwargs["context"]
        self.template_name = template.name

    nav_title = _("Load in IDE")

    @property
    def title(self):
        return 'From panel'

    @property
    def nav_subtitle(self):
        """
        Show abbreviated name of view function as subtitle
        """

        match = resolve(self.toolbar.request.path)
        func, args, kwargs = match
        view_name = get_name_from_obj(func)

        template = loader.get_template('frogpanel/frogtitle.html')
        context = {
            'template_name': self.template_name,
            'view_name': view_name,
        }
        return mark_safe(template.render(context=context))

    template = "frogpanel/frogpanel.html"

    @classmethod
    def get_urls(cls):
        return [
            path("open_template/", views.open_template, name="open_template"),
            path("open_view/", views.open_view, name="open_view"),
        ]

    def enable_instrumentation(self):
        template_rendered.connect(self._store_template_info)

    def disable_instrumentation(self):
        template_rendered.disconnect(self._store_template_info)


