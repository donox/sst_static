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


class BuildObituaries(object):
    # This nikola command creates an html table containing information deceased Sunnyside residents
    # suitable for including in a parent page as a story snippet.  The result output is a page
    # ("obituaries.html") and meta file in the pages directory.

    def __init__(self, logger):
        self.logger = logger
        self.site = None
        self.source_data = PROJECT_PATH + 'support/work_files/obituaries.yaml'
        with open(self.source_data, 'r', encoding='utf-8') as fd:
            yml = YAML(typ='safe')
            self.yml_data = yml.load(fd)
            fd.close()
        self.control = self.yml_data['Processing']
        self.outfiles = None
        self.min_date = None
        self.meta_path = None

    def handler(self, *args, **kwargs):
        self.min_date = dt.datetime.strptime("Jan 1, 2000", '%b %d, %Y')
        self.min_date = dt.datetime.now().date() - dt.timedelta(days=365)
        self.months_two = dt.datetime.now().date() - dt.timedelta(days=61)
        if self.control['Do_All']:
            self.outfiles = WEBSITE_PATH + self.control['Full_Path']
            self.meta_path = self.control['Full_Path']
            self.page_builder(*args, **kwargs)

        if self.control['Do_Snippet']:
            self.outfiles = WEBSITE_PATH + self.control['Snippet_Path']
            self.meta_path = self.control['Snippet_Path']
            self.page_builder(*args, **kwargs)

    def page_builder(self, *args, **kwargs):
        context = {'obits': [],
                   'earlier': []}
        image_no = 1
        for decedent in self.yml_data['Deceased']:
            if not decedent or not decedent['Decedent']['Name']:
                break
            died_short = decedent['Decedent']
            died_short['image'] = '/images/obituraries/inmemoriam-' + str(image_no) + '.jpg'
            image_no += 1
            if image_no > 9:
                image_no = 1
            if 'Date' in died_short.keys():  # ##############################
                try:
                    date_string = died_short['Date']
                    died_dt = parse(date_string)
                    death_date = died_dt.strftime('%b %d, %Y')
                    died_short['Death_date'] = death_date
                    died_short['Death_dt'] = died_dt.date()
                    if self.months_two < died_dt.date():
                        context['obits'].append(died_short)
                    elif self.min_date < died_dt.date():
                        context['earlier'].append(died_short)
                except ValueError as e:
                    self.logger.error(f"Missing or invalid date format for decedent: {died_short['Name']}")

        context['res_count'] = str(len(context['obits']) - 1)
        sorted_deaths = sorted(context['obits'], key=lambda x: x['Death_dt'], reverse=True)
        context['obits'] = sorted_deaths
        env = Environment(
            loader=FileSystemLoader(WEBSITE_PATH + 'plugins/obituaries/templates'),
            autoescape=(['html']))
        template = env.get_template('obituaries.jinja2')
        results = template.render(context).replace('\n', '')
        meta_file = make_meta_file_content('Obituaries', self.meta_path,
                                           description='Obituaries Summary')
        with open(self.outfiles + '.meta', 'w') as meta_fd:
            meta_fd.writelines(meta_file)
            meta_fd.close()
        with open(self.outfiles + '.html', 'w') as html_fd:
            html_fd.write("<span></span>")
            html_fd.writelines(results)
            html_fd.close()


class Obituaries(nikola.plugin_categories.Command):
    name = 'obituaries'
    logger = None

    def __init__(self):
        super(Obituaries, self).__init__()

    def _execute(self, command, args):
        self.logger = get_logger('ping', STDERR_HANDLER)
        converter = BuildObituaries(self.logger)
        converter.handler()
