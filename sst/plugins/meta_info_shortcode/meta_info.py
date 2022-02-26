# -*- coding: utf-8 -*-

from nikola.plugin_categories import ShortcodePlugin
# this is a reference to another package at the same level
import importlib
import re
import os
import platform
import datetime as dt
from conf import PARENT_PATH, PROJECT_PATH, WEBSITE_PATH, SITE_URL


class MetaInfo(ShortcodePlugin):
    # This inserts meta information such as a title or byline into the document.
    name = 'meta_info'

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
        content = content_type = ''
        post = kwargs['post']
        for key in kwargs:
            if key == 'data':
                content = kwargs['data']
            if key == 'info_type':
                content_type = kwargs['info_type']

        folder = post.folder
        post_name = post.post_name
        source_path = post.source_path
        site = kwargs['site']
        deps = []  # WHAT IS THIS FOR

        context = {}
        context['content'] = content
        context['type'] = content_type
        context['permalink'] = '#'
        context.update(self.site.GLOBAL_CONTEXT)
        context.update(kw)
        output = self.site.template_system.render_template(
            'disposition.tmpl',
            None,
            context
        )
        return output, deps

