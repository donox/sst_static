# -*- coding: utf-8 -*-

from nikola.plugin_categories import ShortcodePlugin
# this is a reference to another package at the same level
import importlib
from nikola.utils import get_logger, STDERR_HANDLER
import re
import os
import platform
import datetime as dt
from dateutil import parser
from conf import PARENT_PATH, PROJECT_PATH, WEBSITE_PATH, SITE_URL


class BuildLinksToChildFiles(ShortcodePlugin):
    # This shortcode creates a date sorted list of links to all files in a
    # directory.  It is generally used in an index file (e.g., Stories by Residents)
    # to automatically maintain a time ordered list of content pages.
    name = 'build_links_to_children'

    def __init__(self):
        self.site = None

    def set_site(self, site):
        self.site = site
        # self.inject_dependency('render_posts', 'render_galleries')
        # site.register_shortcode("gallery", self.handler)
        return super().set_site(site)

    def handler(self, *args, **kwargs):
        print("CHILD LINKS CALLED")
        kw = {
            'output_folder': self.site.config['OUTPUT_FOLDER'],
        }
        post = kwargs['post']
        folder = post.folder
        post_name = post.post_name
        source_path = post.source_path
        site = kwargs['site']
        deps = []  # WHAT IS THIS FOR

        # Get list of directories and files in the containing folder.
        #   When called, we are in a file in 'folder' which must itself correspond
        #   to a directory in the same folder.  It is this directory whose contents
        #   must be reflected in the generated result.
        #   (1) for each file (.meta) collect title, date and slug
        #   (2) [NOT NEEDED??] for each directory, find file (already seen) and associate directory with it.
        #       note that directories will have their own list of files and directories.
        #   (3) sort entries by date in descending order
        files_to_display = []
        if source_path.endswith('.md'):
            dir_to_process = source_path[:-3]
            if not os.path.isdir(dir_to_process):
                raise ValueError(f'Attempt to build children of non-directory {dir_to_process}')
        else:
            raise ValueError(f'Attempt to expand non-md file: {source_path}')
        for dirpath, dirnames, filenames in os.walk(dir_to_process):
            for file in filenames:
                if file.endswith('.meta'):
                    meta_data = self.read_meta_file(dirpath + '/' + file)
                    if "path" in meta_data.keys():
                        temp = meta_data['path']
                    else:
                        temp = dirpath
                    if temp.startswith('/'):
                        temp = temp[1:]
                    if temp.endswith('/'):
                        temp = temp[:-1]
                    # NOTE: This is a hack as PythonAnywhere is not properly resolving relative
                    #       URL's.  If fixed, remove next line and change 'abs_slug' to 'slug'
                    #       in child_links.tmpl
                    meta_data['abs_slug'] = SITE_URL + temp + '/' + meta_data['slug'] + '/'
                    # Note: we have to defend against an invalid/incomplete date time format.  We'll assume
                    #       either a valid date or just make today a default.
                    try:
                        res = parser.parse(meta_data['date'])
                    except Exception as e:
                        res = dt.datetime.today()
                    meta_data['date'] = res
                    files_to_display.append(meta_data)

        out_list = sorted(files_to_display,
                          key=lambda x: meta_data['date'], reverse=True)
        context = {}
        context['items'] = out_list
        context['description'] = ''
        context['title'] = ''
        context['lang'] = ''
        context['crumbs'] = []
        context['folders'] = []
        context['permalink'] = '#'
        context.update(self.site.GLOBAL_CONTEXT)
        context.update(kw)
        output = self.site.template_system.render_template(
            'child_links.tmpl',
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
