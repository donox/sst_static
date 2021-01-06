# -*- coding: utf-8 -*-

from nikola.plugin_categories import ShortcodePlugin
# this is a reference to another package at the same level
import importlib
from nikola.utils import get_logger, STDERR_HANDLER
import re
import os
import platform
import datetime as dt
from conf import PARENT_PATH, PROJECT_PATH, WEBSITE_PATH

# NEED TO INSTALL PYTHON SUPPORT FOR IPTC and pull caption, etc from pics
# Also need to do it for gallery - Can we push WP data into pics in prepass?

class Singlepic(ShortcodePlugin):
    name = 'singlepic'

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
        context['width'] = '300px'
        if 'width' in keys:
            context['width'] = kwargs['width']
        if 'w' in keys:
            context['width'] = kwargs['w']
        context['height'] = '300px'
        if 'height' in keys:
            context['height']  = kwargs['height']
        if 'h' in keys:
            context['height']  = kwargs['h']
        context['alignment'] = ''
        if 'align' in keys:
            context['alignment'] = kwargs['align']
        context['image_path'] = ''
        if 'image in keys':
            context['image_path'] = kwargs['image']
        context['caption'] = 'CAPTION'
        context['title'] = 'TITLE'
        context['photographer'] = 'Photographer'
        context['description'] = ''
        context['css_class'] = ''
        context['title_class'] = ''
        context['caption_class'] = ''
        context['image_class'] = ''
        folder = post.folder
        post_name = post.post_name
        source_path = post.source_path
        site = kwargs['site']
        deps = []  # WHAT IS THIS FOR

        context['lang'] = ''
        context['crumbs'] = []
        context['folders'] = []
        context['permalink'] = '#'
        context.update(self.site.GLOBAL_CONTEXT)
        context.update(kw)
        output = self.site.template_system.render_template(
            'singlepic.tmpl',
            None,
            context
        )
        return output, deps

    def read_meta_file(self, filepath):
        res_dict = {}
        re_line = re.compile('\.\. (\w+): (.*)\n')
        # ..wp - status: publish
        with open(filepath, 'r') as fd:
            for line in fd:
                matched_res = re.match(re_line, line)
                try:
                    v1 = matched_res.group(1)
                    v2 = matched_res.group(2)
                    res_dict[v1] = v2
                except Exception as e:
                    print(f'BROKEN LINE?: {line}')
        return res_dict
