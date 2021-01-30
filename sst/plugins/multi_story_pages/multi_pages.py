# -*- coding: utf-8 -*-
import nikola.plugin_categories
# this is a reference to another package at the same level
from nikola.utils import get_logger, STDERR_HANDLER
import re
import os
import json
import datetime as dt
from ruamel.yaml import YAML
from jinja2 import Environment, FileSystemLoader, select_autoescape
# Note that import depends on sys.path and is not properly visible in pycharm
from conf import PARENT_PATH, PROJECT_PATH, WEBSITE_PATH
from plugins.multi_story_pages.process_story_snippet import process_story_snippet
from plugins.multi_story_pages.process_quote import process_quote
from plugins.multi_story_pages.process_html_snippet import process_html_snippet


def run_jinja_template(template, context):
    try:
        env = Environment(
            loader=FileSystemLoader(WEBSITE_PATH + 'sc_templates'),
            autoescape=(['html']))
        template = env.get_template(template)
        results = template.render(context)
        return results
    except Exception as e:
        print(e.args)
        raise e


class Reporter(object):
    def __init__(self, out_file):
        self.outfile = out_file
        self.out_fd = open(PROJECT_PATH + 'support/' + out_file, 'w')
        self.directory = None
        self.file_in_process = None

    def close(self):
        self.out_fd.close()

    def set_directory(self, directory):
        self.directory = directory
        tmp = directory.split('/')[-1]
        self.out_fd.write(f'\n\nFile Directory being processed: {tmp}')
        self.out_fd.write(f'\n   Full path: {directory}')

    def set_file(self, file):
        self.file_in_process = file
        tmp = file.split('/')[-1]
        self.out_fd.write(f'\n\tFile  being processed: {tmp}')
        self.out_fd.write(f'\n\t   Full path: {file}')

    def record_err(self, err_string):
        self.out_fd.write(f'\n\t\tERROR: {err_string}')

    def record_success(self, success_string):
        self.out_fd.write(f'\n\t\tSUCCEED: {success_string}')

    def record_note(self, note):
        self.out_fd.write(f'\n\t\tNOTE: {note}')


class MultiPage(object):
    name = 'multi_pages'

    def __init__(self):
        self.web_source = WEBSITE_PATH + '/pages'
        self.yaml_dir = WEBSITE_PATH + 'plugins/multi_story_pages/pages'
        self.content_dict = {}
        self.site = None
        search_path = WEBSITE_PATH + '/plugins/multi_story_pages/templates'
        template_loader = FileSystemLoader(searchpath=search_path)
        self.template_environment = Environment(loader=template_loader)
        self.reporter = Reporter('multi_page.txt')

    def _make_column_width_classes(self, width):
        sizes = ['col-', 'col-sm-', 'col-md-', 'col-lg-', 'col-xl-']
        width_str = str(width)
        return ' '.join([x + width_str for x in sizes])

    def set_site(self, site):
        self.site = site
        # self.inject_dependency('render_posts', 'render_galleries')
        # site.register_shortcode("gallery", self.handler)
        return super().set_site(site)

    def _yaml_iterator(self, yaml_page, context):
        try:
            context['rows'] = []
            for rownum, row in enumerate(yaml_page['Rows']):
                row_context = {}
                context['rows'].append(row_context)
                row_context['cols'] = []
                if row['Row']:
                    for colnum, col in enumerate(row['Row']):
                        col_context = {}
                        col_keys = list(col.keys())
                        row_context['cols'].append(col_context)
                        col_context['entries'] = []
                        if 'Width' in col_keys:
                            wd = col['Width']
                        else:
                            wd = 4
                        col_context['col_width'] = self._make_column_width_classes(wd)
                        if col['Entries']:
                            for entrynum, entry in enumerate(col['Entries']):
                                entry_context = {}
                                col_context['entries'].append(entry_context)
                                yield rownum, colnum, entrynum, entry_context, entry['Entry']
        except Exception as e:
            raise ValueError(f"Invalid key in yaml page {yaml_page}")

    def _yaml_entry(self, yaml_page):
        with open(yaml_page, 'r', encoding='utf-8') as fd:
            try:
                self.reporter.set_file(yaml_page)
                yml = YAML(typ='safe')
                return yml.load(fd)
            except Exception as e:
                raise ValueError(f"Failure loading yaml entry: {yaml_page} with error: {e}")

    def get_pages_to_build_yaml(self):
        for dirpath, _, fileList in os.walk(self.yaml_dir):
            dir_control_file = dirpath.split('/')[-1]
            dir_yaml = dirpath + '/' + dir_control_file + '.yaml'
            if os.path.exists(dir_yaml):
                with open(dir_yaml, 'r', encoding='utf-8') as fd:
                    try:
                        self.reporter.set_directory(dirpath)
                        yml = YAML(typ='safe')
                        yield dirpath, yml.load(fd)
                    except Exception as e:
                        raise ValueError(f"Failure loading {dir_yaml} with error: {e}")

    def handler(self, *args, **kwargs):
        for page_dir, special_page in self.get_pages_to_build_yaml():
            context = {}  # Each file is a separately built page
            for row_num, col_num, entry_num, local_context, entry in self._yaml_iterator(special_page, context):
                position = (row_num, col_num, entry_num)
                if type(entry) == str:
                    entry_descriptor = entry + '.yaml'
                    entry_page_path = page_dir + '/' + entry_descriptor
                    if not os.path.exists(entry_page_path):
                        err_string = f"File missing in {page_dir} for file: {entry_descriptor}"
                        self.reporter.record_err(err_string)
                    try:
                        entry = self._yaml_entry(entry_page_path)['Entry']
                        entry_type = entry['entry_type']
                    except Exception as e:
                        err_string = f"Invalid YAML - missing expected key in {entry.keys()}"
                        self.reporter.record_err(err_string)
                elif type(entry) == dict:
                    entry_type = entry['entry_type']
                else:
                    err_string = 'Unrecognized Entry Type: {type(entry)} for entry: {entry}'
                    self.reporter.record_err(err_string)
                    entry_type = None
                if entry_type:
                    try:
                        if entry_type == 'story_snippet':
                            res = process_story_snippet(entry, position, self.site, self.template_environment,
                                                        self.reporter)
                        elif entry_type == 'quote':
                            res = process_quote(entry, position, self.site, self.template_environment)
                        elif entry_type == 'story_snippet':
                            foo = 3
                        elif entry_type == 'html_snippet':
                            res = process_html_snippet(entry, position, self.site, self.template_environment,
                                                        self.reporter)
                        else:
                            err_string = "Unrecognized YAML entry_type: {entry_type}"
                            self.reporter.record_err(err_string)
                        if res:
                            local_context['content'] = res
                            local_context['entry_type'] = entry_type
                            local_context['width_class'] = ''
                            local_context['title_class'] = ''
                            local_context['caption_class'] = ''
                            local_context['image_class'] = ''
                            # post = kwargs['post']             # Not valid unless shortcode???
                            # folder = post.folder
                            # post_name = post.post_name
                            # source_path = post.source_path
                    except Exception as e:
                        err_string = f'Error from element processing: {e}'
                        self.reporter.record_err(err_string)
            template = self.template_environment.get_template('page_layout.jinja2')
            output = template.render(**context)
            output = [x + '\n' for x in output.split('\n') if x.strip()]        # kill excess blank space
            page_slug = page_dir.split('/pages/')[-1]
            # ToDo: page_loc does not deal with non-top-level pages
            page_loc = WEBSITE_PATH + 'pages/' + page_slug
            # NOTE:  Write out as html file - it will be loaded without further processing.
            with open(page_loc + '.md', 'w+') as fd_out:
                fd_out.writelines(output)
                fd_out.close
                self.reporter.record_success(f'{page_slug} md file written')
            with open(page_loc + '.meta', 'w+') as fd_out:
                fd_out.writelines(f"..title: yyy\n")
                fd_out.writelines(f"..slug: {page_slug}\n")
                tmp = dt.datetime.now().strftime("%Y-%m-%d")
                fd_out.writelines(f"..date: {tmp}\n")
                fd_out.writelines(f"..description: yyy\n")
                fd_out.close()
                self.reporter.record_success(f'{page_slug} meta file written')
            # Save output to file with meta file
        self.reporter.close()
        return


converter = MultiPage()


class MultiStoryPages(nikola.plugin_categories.Command):
    name = 'multi_pages'
    logger = None

    def __init__(self):
        super(MultiStoryPages, self).__init__()

    def _execute(self, command, args):
        self.logger = get_logger('ping', STDERR_HANDLER)
        converter.handler()
