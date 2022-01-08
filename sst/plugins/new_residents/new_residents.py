# -*- coding: utf-8 -*-

from nikola.plugin_categories import ShortcodePlugin
from nikola.utils import get_logger, STDERR_HANDLER
import nikola.plugin_categories
from conf import PROJECT_PATH, WEBSITE_PATH
from ruyaml import YAML
from jinja2 import Environment, FileSystemLoader
from utilities.meta_files import make_meta_file_content


class BuildNewResidents(object):
    # This nikola command creates an html table containing information on new Sunnyside residents
    # suitable for including in a parent page as a story snippet.  The result output is a page
    # ("new-residents.html") and meta file in the pages directory.

    def __init__(self):
        self.site = None
        self.source_data = PROJECT_PATH + 'support/work_files/new_residents.yaml'
        self.outfiles = WEBSITE_PATH + 'pages/new-residents'
        self.profile_directory = '/pages/cool-stories-index/new-resident-profiles/'
        with open(self.source_data, 'r', encoding='utf-8') as fd:
            yml = YAML(typ='safe')
            self.yml_data = yml.load(fd)
            fd.close()

    def handler(self, *args, **kwargs):
        context = {'residents': self.yml_data['Residents']}
        context['res_count'] = str(len(context['residents'])-1)
        for resident in context['residents']:
            if 'Profile' in resident['Resident'].keys() and resident['Resident']['Profile']:
                full_path = self.profile_directory + resident['Resident']['Profile'] + '/'
                resident['Resident']['Profile'] = full_path
        env = Environment(
            loader=FileSystemLoader(WEBSITE_PATH + 'plugins/new_residents/templates'),
            autoescape=(['html']))
        template = env.get_template('new_residents.tmpl')
        results = template.render(context).replace('\n','')
        meta_file = make_meta_file_content('New Residents', 'new-residents',
                                           description='New Resident links content for Page One')
        with open(self.outfiles+'page-one.meta', 'w') as meta_fd:
            meta_fd.writelines(meta_file)
            meta_fd.close()
        with open(self.outfiles+'.html', 'w') as html_fd:
            html_fd.write("<span></span>")
            html_fd.write('<a id="newRes"></a>')
            html_fd.writelines(results)
            html_fd.close()


converter = BuildNewResidents()


class NewResidents(nikola.plugin_categories.Command):
    name = 'new_residents'
    logger = None

    def __init__(self):
        super(NewResidents, self).__init__()

    def _execute(self, command, args):
        self.logger = get_logger('ping', STDERR_HANDLER)
        converter.handler()
