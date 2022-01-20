# -*- coding: utf-8 -*-

from nikola.plugin_categories import ShortcodePlugin
from blinker import signal
import re
import datetime as dt

class Disposition(ShortcodePlugin):
    # This reads disposition info from the meta file of the post and processes it.
    name = 'disposition'

    def __init__(self):
        self.site = None

    def set_site(self, site):
        self.site = site
        return super().set_site(site)

    def handler(self, *args, **kwargs):
        kw = {
            'output_folder': self.site.config['OUTPUT_FOLDER'],
        }
        context = {}
        post = kwargs['post']
        for key in kwargs:
            if key == 'remove_date':                            # Not useful - record in meta file or something
                context['remove_date'] = kwargs['remove_date']
            if key == 'post_date':
                context['post_date'] = kwargs['post_date']
            if key == 'on_remove':                              # Not useful - need to process somehow
                context['on_remove'] = kwargs['on_remove']

        folder = post.folder
        post_name = post.post_name
        source_path = post.source_path
        site = kwargs['site']
        deps = []  # WHAT IS THIS FOR

        context['permalink'] = '#'
        context.update(self.site.GLOBAL_CONTEXT)
        context.update(kw)
        output = self.site.template_system.render_template(
            'disposition.tmpl',
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
