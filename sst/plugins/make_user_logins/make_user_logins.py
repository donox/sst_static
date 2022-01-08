# -*- coding: utf-8 -*-

import nikola.plugin_categories
# this is a reference to another package at the same level
import importlib
from nikola.utils import get_logger, STDERR_HANDLER
import csv
from hashlib import md5

import platform
from conf import PARENT_PATH, PROJECT_PATH, WEBSITE_PATH

class MakeUserLogins(object):
    def __init__(self):
        self.web_source = WEBSITE_PATH + '/pages'
        self.file_in = PROJECT_PATH + 'support/users.csv'
        self.file_out = PROJECT_PATH + 'sst/themes/sst/assets/js/user_logins.js'
        self.default_password = 'Sunny'
        self.default_md5_password = md5(self.default_password.encode('utf-8')).hexdigest()

    def close(self):
        pass

    def make_logins(self):
        with open(self.file_in, 'r') as fd_in:
            reader = csv.reader(fd_in)
            with open(self.file_out, 'w+') as fd_out:
                password_table = 'var user_logins = {\n'
                for line in reader:
                    if len(line) == 1:
                        pass_out = self.default_md5_password
                    else:
                        pass_out = md5(line[1].encode('utf-8')).hexdigest()
                    user_out = md5(line[0].encode('utf-8')).hexdigest()
                    password_table += '"' + user_out + '": "' + pass_out + '",\n'
                password_table = password_table[:-2] + '}\n'
                fd_out.write(password_table)
            fd_out.close()
            fd_in.close()


    def file_reader(self):
        for line in self.content_dict['fixes']:
            yield line

converter = MakeUserLogins()


class MakeLogins(nikola.plugin_categories.Command):
    name = 'make_user_logins'
    logger = None

    def __init__(self):
        super(MakeLogins, self).__init__()

    def _execute(self, command, args):
        self.logger = get_logger('ping', STDERR_HANDLER)
        converter.make_logins()
