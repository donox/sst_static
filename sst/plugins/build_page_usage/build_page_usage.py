# -*- coding: utf-8 -*-
import os
import re

from nikola.plugin_categories import ShortcodePlugin
from nikola.utils import get_logger, STDERR_HANDLER
import nikola.plugin_categories
from conf import PROJECT_PATH, WEBSITE_PATH
from jinja2 import Environment, FileSystemLoader
from utilities.meta_files import make_meta_file_content
import config_private as pvt
import shutil


class PageUsage(object):
    # This command creates admin pages showing pages in use and where they are used
    # along with those no longer in use.
    page_ref_re = re.compile(r'href="([a-zA-Z0-9-/._]+)"')
    conf_ref_re = re.compile(r'"/(pages/[a-zA-Z0-9-/._]+)"')

    def __init__(self):
        self.site = None
        self.galleries_dir = PROJECT_PATH + 'sst/galleries'
        self.images_dir = PROJECT_PATH + 'sst/images'
        self.pages_dir = PROJECT_PATH + 'sst/output/pages'
        self.outfiles_dir = PROJECT_PATH + 'sst/pages/admin'
        self.pages = dict()
        self.pages_touched = set()

    def handler(self, *args, **kwargs):
        # Build context for creating display pages with jinja templates
        context = {'all_pages': self.pages, }

        # Create page list with a dictionary giving the info about pages it references,
        # pages that reference it, whether referenced from menubar, ...
        # We process in the output directory to pages after all shortcodes have been expanded.
        for root, dirs, files in os.walk(self.pages_dir):
            short_path = root.split('/sst/output/')[1]  # this is also the file_name as it is a directory of index.xx
            for file in files:
                if file == 'index.html':
                    if short_path not in self.pages_touched:  # This allows for two pages
                        # with same name in different directories
                        this_entry = self._add_dict_entry(short_path)
                    else:
                        this_entry = self.pages[short_path]
                    with open(root + '/index.html', 'r') as in_file:
                        file_content = in_file.read()
                        in_file.close()
                    start = file_content.find('<article')
                    if start == -1:
                        foo = 3
                    end = file_content.find('</article')
                    if end == -1:
                        foo = 3
                    file_content = file_content[start:end]
                    for file_ref in re.findall(PageUsage.page_ref_re, file_content):
                        if 'images/' not in file_ref and 'galleries/' not in file_ref:
                            full_ref = self.make_path_name(short_path, file_ref)
                            if full_ref not in self.pages_touched:
                                new_entry = self._add_dict_entry(full_ref)
                            else:
                                new_entry = self.pages[full_ref]
                            this_entry['references_to'].append(full_ref)
                            new_entry['referenced_by'].append(short_path)
                    with open(PROJECT_PATH + 'sst/conf.py', 'r') as in_file:
                        conf = ''.join(in_file.readlines())
                        in_file.close()
                    start = conf.find('NAVIGATION_LINKS')
                    conf = conf[start:]
                    end = conf.find('Alternative')
                    conf = conf[:end]
                    for path in re.findall(PageUsage.conf_ref_re, conf):
                        if path not in self.pages:
                            self._add_dict_entry(path)
                        self.pages[path]['in_menu'] = True

        all_pages_to_sort = sorted(list(self.pages.items()), key=lambda x: x[0])
        context['page_list'] = all_pages_to_sort

        env = Environment(
            loader=FileSystemLoader(WEBSITE_PATH + 'plugins/build_page_usage/templates'),
            autoescape=(['html']))

        template = env.get_template('build_page_usage.jinja2')
        results = template.render(context).replace('\n', '')
        results = re.sub(" None", " ", results)  # remove occurrences of 'None'
        results = re.sub(" +", " ", results)  # remove excess whitespace
        meta_file = make_meta_file_content('Page References', 'page_references',
                                           description='References between pages')
        with open(self.outfiles_dir + '/pages_references.meta', 'w') as meta_fd:
            meta_fd.writelines(meta_file)
            meta_fd.close()
        with open(self.outfiles_dir + '/pages_references.html', 'w') as html_fd:
            html_fd.writelines(results)
            html_fd.close()

    def _add_dict_entry(self, path):
        self.pages[path] = {"references_to": [],
                            "referenced_by": [],
                            "in_menu": False,
                            }
        self.pages_touched.add(path)
        return self.pages[path]

    def make_path_name(self, root, page):
        """Convert page name by removing segments from root corresponding to '..'"""
        root_split = root.split('/')
        page_split = page.split('/')
        for seg in page_split:
            if seg == '..':
                root_split.pop()
                page_split.pop(0)
            else:
                break
        rs = "/".join(root_split)
        ps = "/".join(page_split)
        return rs + '/' + ps


converter = PageUsage()


class BuildPageUsage(nikola.plugin_categories.Command):
    name = 'build_page_usage'
    logger = None

    def __init__(self):
        super(BuildPageUsage, self).__init__()

    def _execute(self, command, args):
        self.logger = get_logger('ping', STDERR_HANDLER)
        converter.handler()
