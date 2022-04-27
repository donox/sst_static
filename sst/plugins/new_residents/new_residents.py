# -*- coding: utf-8 -*-

from nikola.plugin_categories import ShortcodePlugin
from nikola.utils import get_logger, STDERR_HANDLER
import nikola.plugin_categories
from conf import PROJECT_PATH, WEBSITE_PATH
from ruyaml import YAML
from jinja2 import Environment, FileSystemLoader
from utilities.meta_files import make_meta_file_content
import datetime as dt
from dateutil.parser import parse


class BuildNewResidents(object):
    # This nikola command creates an html table containing information on new Sunnyside residents
    # suitable for including in a parent page as a story snippet.  The result output is a page
    # ("new-residents.html") and meta file in the pages directory.

    def __init__(self, logger):
        self.logger = logger
        self.site = None
        self.source_data = PROJECT_PATH + 'support/work_files/new_residents.yaml'
        with open(self.source_data, 'r', encoding='utf-8') as fd:
            yml = YAML(typ='safe')
            self.yml_data = yml.load(fd)
            fd.close()
        self.control = self.yml_data['Processing']
        self.outfiles = None
        self.min_date = None
        self.meta_path = None

    def handler(self, *args, **kwargs):
        if self.control['Do_All']:
            self.outfiles = WEBSITE_PATH + self.control['Full_Path']
            self.min_date = dt.datetime.strptime("Jan 1, 2000", '%b %d, %Y')
            self.meta_path = self.control['Full_Path']
            self.page_builder(*args, **kwargs)

        if self.control['Do_Snippet']:
            self.outfiles = WEBSITE_PATH + self.control['Snippet_Path']
            self.min_date = dt.datetime.strptime(self.control['Min_Date'], '%b %d, %Y')
            self.meta_path = self.control['Snippet_Path']
            self.page_builder(*args, **kwargs)

    def page_builder(self, *args, **kwargs):
        context = {'residents': []}
        for resident in self.yml_data['Residents']:
            if not resident or resident == '':
                break
            resid_short = resident['Resident']
            if 'Arrived' in resid_short.keys():           # ##############################
                try:
                    date_string = resid_short['Arrived']
                    arrival_dt = parse(date_string)
                    arrival_date = arrival_dt.strftime('%b %d, %Y')
                    resid_short['Arrived_date'] = arrival_date
                    resid_short['Arrive_dt'] = arrival_dt
                    if self.min_date < arrival_dt:
                        context['residents'].append(resident)
                except ValueError as e:
                    self.logger.error(f"Missing or invalid date format for resident: {resid_short['Name']}")
        context['res_count'] = str(len(context['residents']) - 1)
        sorted_residents = sorted(context['residents'], key=lambda x: x['Resident']['Arrive_dt'])
        context['residents'] = sorted_residents
        env = Environment(
            loader=FileSystemLoader(WEBSITE_PATH + 'plugins/new_residents/templates'),
            autoescape=(['html']))
        template = env.get_template('new_residents.jinja2')
        results = template.render(context).replace('\n', '')
        meta_file = make_meta_file_content('New Residents', self.meta_path,
                                           description='New Resident Summary')
        with open(self.outfiles+'.meta', 'w') as meta_fd:
            meta_fd.writelines(meta_file)
            meta_fd.close()
        with open(self.outfiles+'.html', 'w') as html_fd:
            html_fd.write("<span></span>")
            html_fd.writelines(results)
            html_fd.close()





class NewResidents(nikola.plugin_categories.Command):
    name = 'new_residents'
    logger = None

    def __init__(self):
        super(NewResidents, self).__init__()

    def _execute(self, command, args):
        self.logger = get_logger('ping', STDERR_HANDLER)
        converter = BuildNewResidents(self.logger)
        converter.handler()
