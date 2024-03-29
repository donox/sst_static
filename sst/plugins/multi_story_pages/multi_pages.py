# -*- coding: utf-8 -*-
import nikola.plugin_categories
# this is a reference to another package at the same level
from nikola.utils import get_logger, STDERR_HANDLER
import re
import os
import shutil
import datetime as dt
from ruyaml import YAML
from jinja2 import Environment, FileSystemLoader, select_autoescape
# Note that import depends on sys.path and is not properly visible in pycharm
from conf import PARENT_PATH, PROJECT_PATH, WEBSITE_PATH
from plugins.multi_story_pages.process_story_snippet import process_story_snippet
from plugins.multi_story_pages.process_quote import process_quote
from plugins.multi_story_pages.process_html_snippet import process_html_snippet
from plugins.multi_story_pages.process_eye_catcher import process_eye_catcher


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


class MultiPage(object):
    '''Process pages consisting of multiple stories with configuration specified in yaml file.'''
    name = 'multi_pages'

    def __init__(self, logger):
        self.logger = logger
        self.date_string = dt.datetime.today().date().isoformat()
        self.yaml_dir = PROJECT_PATH + 'support/multi_story_pages/pages/'
        self.content_dict = {}
        self.site = None
        self.preamble = []    # Will contain list of tags at top of page to link to places within page
        search_path = WEBSITE_PATH + '/plugins/multi_story_pages/templates'
        template_loader = FileSystemLoader(searchpath=search_path)
        self.template_environment = Environment(loader=template_loader)

    def _make_column_width_classes(self, width):
        """Make bootstrap width classes (e.g., col-sm-4) for specified width"""
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
            try:
                back_color = yaml_page['Background']
                context['background_color'] = back_color
            except KeyError:
                context['background_color'] = "#fff"
            for rownum, row in enumerate(yaml_page['Rows']):
                row_context = {}
                context['rows'].append(row_context)
                row_context['cols'] = []
                key = 'Row'             # Track key used in case of error
                if row[key]:
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
                        col_context['col_count'] = wd            # pass $ columns to support calculations within entry
                        key = 'Entries'
                        if col[key]:
                            for entrynum, entry in enumerate(col['Entries']):
                                entry_context = dict()
                                entry_context['parent_col'] = col_context
                                entry_context['col_num'] = colnum
                                entry_context['parent_row'] = row_context
                                col_context['entries'].append(entry_context)
                                key = 'Entry'
                                yield rownum, colnum, entrynum, entry_context, entry[key]
        except Exception as e:
            self.logger.error(f"Invalid key {key} in yaml page {yaml_page}")

    def _yaml_entry(self, yaml_page):
        with open(yaml_page, 'r', encoding='utf-8') as fd:
            try:
                yml = YAML(typ='safe')
                return yml.load(fd)
            except Exception as e:
                self.logger.error(f"Failure loading yaml entry: {yaml_page} with error: {e}")

    def get_pages_to_build_yaml(self):
        """Iterator for yaml files for each multi_page to be built."""
        # Note - the first path tested is for the yaml_dir itself which will not have
        #        an associated yaml file, to the loop skips before processing a specific page directory.
        for dirpath, _, fileList in os.walk(self.yaml_dir):
            dir_control_file = dirpath.split('/')[-1]
            if dir_control_file != '':
                dir_yaml = dirpath + '/' + dir_control_file + '.yaml'
                if os.path.exists(dir_yaml):
                    with open(dir_yaml, 'r', encoding='utf-8') as fd:
                        try:
                            yml = YAML(typ='safe')
                            yield dirpath, yml.load(fd)
                        except Exception as e:
                            self.logger.error(f"Failure loading {dir_yaml} with error: {e.args}")
                else:
                    self.logger.info(f"Attempted to find {dir_yaml} which does not exist - skipping.")

    def _process_entry(self, entry_type, local_context, entry, position):
        if "target" in entry.keys():
            target = entry["target"]    # arbitrary string as content of anchor
            target_address = "#target_" + str(len(self.preamble) + 1)
            target_html = f'<a href="{target_address}"> {target} </a>'
            self.preamble.append(target_html)
        entry['parent_context'] = local_context        # to allow entry to determine surroundings (esp. width as # cols)
        if entry_type == 'story_snippet':
            res = process_story_snippet(entry, position, self.site, self.template_environment,
                                        self.logger)
        elif entry_type == 'eye_catcher':
            res = process_eye_catcher(entry, position, self.site, self.template_environment, self.logger)
        elif entry_type == 'quote':
            res = process_quote(entry, position, self.site, self.template_environment)
        elif entry_type == 'html_snippet':
            res = process_html_snippet(entry, position, self.site, self.template_environment,
                                       self.logger)
        else:
            err_string = "Unrecognized YAML entry_type: {entry_type}"
            self.logger.error(err_string)
        if res:
            local_context['content'] = res
            local_context['entry_type'] = entry_type
            local_context['width_class'] = ''
            local_context['title_class'] = ''
            local_context['caption_class'] = 'caption'
            local_context['image_class'] = ''
            # post = kwargs['post']             # Not valid unless shortcode???
            # folder = post.folder
            # post_name = post.post_name
            # source_path = post.source_path
            if "goback" in entry.keys():
                local_context['goback'] = f'<a href="#Top"><span style="color: #00ccff;">To: {entry["goback"]}</span></a>'

    def handler(self, *args, **kwargs):
        for page_dir, special_page in self.get_pages_to_build_yaml():
            context = {}  # Each file is a separately built page
            for row_num, col_num, entry_num, local_context, entry in self._yaml_iterator(special_page, context):
                entry_type = None  # defend against undefined variable
                position = (row_num, col_num, entry_num)
                if type(entry) == str:
                    entry_descriptor = entry + '.yaml'
                    entry_page_path = page_dir + '/' + entry_descriptor
                    if not os.path.exists(entry_page_path):
                        err_string = f"File missing in {page_dir} for file: {entry_descriptor}"
                        self.logger.error(err_string)
                    try:
                        entry = self._yaml_entry(entry_page_path)['Entry']
                        entry_type = entry['entry_type']
                    except Exception as e:
                        if entry_type:
                            if entry_type.find('-') != -1:
                                err_string = f"Do you have a '-' instead of a '_' in the entry {entry}?"
                            else:
                                err_string = f"Invalid YAML - missing expected key in {entry.keys()}"
                        else:
                            err_string = f"YAML entry {entry} has no defined 'entry_type"
                        self.logger.error(err_string)

                elif type(entry) == dict:
                    entry_type = entry['entry_type']
                else:
                    err_string = 'Unrecognized Entry Type: {type(entry)} for entry: {entry}'
                    self.logger.error(err_string)
                    entry_type = None
                if entry_type:
                    try:
                        self._process_entry(entry_type, local_context, entry, position)
                    except Exception as e:
                        err_string = f'Error from element processing: {e}'
                        self.logger.error(err_string)
            context["preamble"] = self.preamble
            template = self.template_environment.get_template('page_layout.jinja2')
            output = template.render(**context)
            output = [x.strip() + '\n' for x in output.split('\n') if x.strip()]        # kill excess blank space
            page_slug = page_dir.split('/pages/')[-1]
            # ToDo: page_loc does not deal with non-top-level pages
            page_loc = WEBSITE_PATH + 'pages/' + page_slug
            # NOTE:  Write out as html file - it will be loaded without further processing.
            with open(page_loc + '.md', 'w+') as fd_out:
                fd_out.writelines(output)
                fd_out.close
                self.logger.info(f'{page_slug} md file written')
            with open(page_loc + '.meta', 'w+') as fd_out:
                fd_out.writelines(f"..title: yyy\n")
                fd_out.writelines(f"..slug: {page_slug}\n")
                tmp = dt.datetime.now().strftime("%Y-%m-%d")
                fd_out.writelines(f"..date: {tmp}\n")
                fd_out.writelines(f"..description: yyy\n")
                fd_out.close()
                self.logger.info(f'{page_slug} meta file written')
            # Save output to file with meta file
        return





class MultiStoryPages(nikola.plugin_categories.Command):
    name = 'multi_pages'
    logger = None

    def __init__(self):
        super(MultiStoryPages, self).__init__()

    def _execute(self, command, args):
        self.logger = get_logger('multi-page', STDERR_HANDLER)
        converter = MultiPage(self.logger)
        converter.handler()

