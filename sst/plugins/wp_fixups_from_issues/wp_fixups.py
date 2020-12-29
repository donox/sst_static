# -*- coding: utf-8 -*-

import nikola.plugin_categories
# this is a reference to another package at the same level
import importlib
from nikola.utils import get_logger, STDERR_HANDLER
import re
import os
from urllib.parse import urlparse
from jinja2 import Environment, FileSystemLoader, select_autoescape
import shutil
from functools import reduce
from operator import mul

import platform

OXLEY_PATH = '/home/don/PycharmProjects'
OXLEY_PATH = '../../../'
# IONOS_PATH = '~/homepages/11/d835068234/htdocs/'
IONOS_PATH = '../../'
PATTERSON_PATH = '../../../'

os.environ['OPENBLAS_NUM_THREADS'] = '1'  # SOME ISSUE SPAWNING PROCESSES - Bad fix????

node = platform.node()
PARENT_PATH = IONOS_PATH                # Is this still right after moving convert_shortcodes??????????????????????
if node == 'Descartes':
    PARENT_PATH = OXLEY_PATH + 'PycharmProjects/'
PROJECT_PATH = PARENT_PATH + 'sst_static/'
WEBSITE_PATH = PARENT_PATH + 'sst_static/sst/'


# def run_jinja_template(template, context):
#     try:
#         env = Environment(
#             loader=FileSystemLoader(WEBSITE_PATH + 'sc_templates'),
#             autoescape=(['html']))
#         template = env.get_template(template)
#         results = template.render(context)
#         return results
#     except Exception as e:
#         print(e.args)
#         raise e


class WpFixups(object):
    # available_shortcodes = ['maxbutton', 'singlepic', 'src_singlepic', 'ngg_images', 'src_slideshow', 'child-pages']
    # unhandled_shortcodes = ['ultimatemember', 'ultimatemember_account', 'wp_google_search', 'srcp_wellness_center',
    #                         'srcp_wellness_individual', 'srcp_wellness_statistics', 'src_lists_membership',
    #                         'src_lists_admin_functions', 'catlist', 'sustainability', 'includeme',
    #                         'thermometer', 'ninja_forms', 'src_manage_opportunity', 'src_record_registration',
    #                         'src_sign_up_for_opportunity', 'src_list_opportunities', 'src_register_opportunity',
    #                         'src_create_opportunity', 'src_fwf_notify', 'nggallery', 'ngg', 'srcp_club_membership']
    # We support two flavors of argument list:
    # (1) The value of an individual argument is surrounded by quotes (' or ")
    # (2) The value of an argument is a single character string [a-zA-Z_]
    # -- the argument types may not be mixed.

    # Note that the "^]]" below defends against a left bracket immediately following a shortcode
    sc_re = re.compile(r'\[([a-zA-Z0-9\-]+) *(\w+=[^\]]+)* *\]', re.I)
    sc_re_arg = re.compile(r'( *([A-Za-z0-9_]+) *= *"(.*)")+?')
    sc_re_arg_no_quotes = re.compile(r'( *([A-Za-z0-9_]+) *= *(.[a-zA-Z_]+))+?')

    def __init__(self):
        self.web_source = WEBSITE_PATH + '/pages'
        self.content_dict = {}
        self.content_dict['fixes'] = open(PROJECT_PATH + 'support/fixes.txt', 'r')

    def close(self):
        if self.content_dict['bad']:
            self.content_dict['bad'].close()
            self.content_dict['bad'] = None
        self.content_dict['issues'].close()

    def process_pages(self):
        for dirpath, _, fileList in os.walk(self.web_source):
            # print('Process directory: %s' % dirpath)
            for fname in fileList:
                if fname in self.dead_files:
                    try:
                        self.content_dict['issues'].writelines(
                            f"DEAD FILE: (???): {self.content_dict['file_path']} \n\n")
                    except Exception as e:
                        foo = 3
                if fname not in self.dead_files and \
                        fname.endswith('.md') and \
                        not fname.startswith('veteran') and \
                        not dirpath.endswith('-notes'):    # and \
                        # fname == 'resident-told-stories.md':
                    file_path = os.path.join(dirpath, fname)
                    self.content_dict['file_path'] = file_path
                    # print(file_path)
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        self.shortcode_string = ''.join(infile.readlines())
                        current_string = self.parse_a_tag(self.shortcode_string)
                        result_string = ''
                        while current_string:
                            res = self.parse_shortcode(current_string)
                            if res == 'SHORTCODE ARG FAILURE':
                                # print(f'Shortcode failure in: {file_path}')
                                self.content_dict['issues'].writelines(f'SHORTCODE FAILURE: in: {file_path}\n\n')
                                current_string = ''
                            elif res:
                                if res['start']:
                                    # if start is not at front of string, add start of string to result
                                    result_string += current_string[:res['start']]
                                current_string = current_string[res['end']:]
                                self.content_dict['count_slash'] = file_path.count('/')  # path depth for relative refs
                                tmp = self._process_shortcode(res)
                                if tmp == 'PARSE FAILURE':
                                    result_string += 'SHORTCODE NOT YET HANDLED: ' + current_string
                                    self.content_dict['issues'].writelines(f"UNHANDLED SHORTCODE: {file_path}\n\n")
                                elif tmp:
                                    result_string += tmp
                            else:
                                result_string += current_string
                                current_string = ''
                    with open(file_path, 'w') as outfile:
                        outfile.write(result_string)
        print('Unhandled Shortcodes')
        for sc in self.unhandled:
            print(sc)
        self.close()

    def file_reader(self):
        for line in self.content_dict['fixes']:
            yield line

    def fix_inputs(self):
        n = 0
        for line in self.file_reader():
            n += 1
            end_cmd = line.find(':')
            if end_cmd == -1:
                pass
            else:
                cmd = line[:end_cmd]
                args = line[end_cmd+1:]
                if cmd == 'DEAD FILE':
                    self.dead_file(args)
                elif cmd == 'UNHANDLED SHORTCODE':
                    while line.find('++') == -1:
                        line = next(self.file_reader())
                        n += 1
                        args += line
                    self.unhandled_shortcode(args)
                elif cmd == 'foo':
                    pass
                elif cmd == 'foo':
                    pass
                elif cmd == 'foo':
                    pass
                else:
                    raise ValueError(f'Unrecognized command: {cmd}')

    def dead_file(self, args):
        file_path = args.split(':')[-1][:-1]    # pick out path and remove \n
        if os.path.isfile(os.path.abspath(PARENT_PATH + file_path)):
            print(f'Delete: {file_path}')

    def unhandled_shortcode(self, args):
        arg_list = args.split(':')
        file_path_lst = arg_list[1].split(' ')
        while len(file_path_lst) > 0 and len(file_path_lst[0]) == 0:
            file_path_lst = file_path_lst[1:]
        file_path = file_path_lst[0]
        shortcode_segment = arg_list[2]
        print(f'Unhandled shortcode in {file_path}')

    def dead_filex(self, args):
        pass

    def dead_filec(self, args):
        pass

    def dead_filev(self, args):
        pass


converter = WpFixups()


class FixCode(nikola.plugin_categories.Command):
    name = 'wp_fixups'
    logger = None

    def __init__(self):
        super(FixCode, self).__init__()

    def _execute(self, command, args):
        self.logger = get_logger('ping', STDERR_HANDLER)
        converter.fix_inputs()
