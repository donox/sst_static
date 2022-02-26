# -*- coding: utf-8 -*-

from nikola.plugin_categories import ShortcodePlugin
# this is a reference to another package at the same level
import importlib
import re
import os
import platform
import datetime as dt
from conf import PARENT_PATH, PROJECT_PATH, WEBSITE_PATH, SITE_URL


class Links(ShortcodePlugin):
    #  A shortcode to insert links ("a" tag) info for downloads, urls, etc
    name = 'links'

    def __init__(self):
        self.site = None

    def set_site(self, site):
        self.site = site
        # self.inject_dependency('render_posts', 'render_galleries')
        # site.register_shortcode("gallery", self.handler)
        return super().set_site(site)

    def handler(self, *args, **kwargs):
        kw = {
            'output_folder': self.site.config['OUTPUT_FOLDER'],
        }
        context = {}
        keys = kwargs.keys()
        post = kwargs['post']

        if "purpose" not in keys:
            raise ValueError(f"No key \"purpose\" found in links shortcode.")
        purpose = kwargs["purpose"]
        context["purpose"] = purpose
        if "reference" not in keys:
            raise ValueError(f"No key \"reference\" found in links shortcode.")
        reference = kwargs["reference"]
        target = None
        if "target" in keys:
            target = kwargs["target"]
        button = "DOWNLOAD"
        context["button"] = button
        if purpose == "download":
            file_path = "files/" + reference
            if not os.path.exists(file_path):
                raise ValueError(f"No document found at location {reference}")
            context["href"] = reference
        deps = []  # WHAT IS THIS FOR
        context.update(self.site.GLOBAL_CONTEXT)
        context.update(kw)
        output = self.site.template_system.render_template(
            'links.tmpl',
            None,
            context
        )
        return output, deps

