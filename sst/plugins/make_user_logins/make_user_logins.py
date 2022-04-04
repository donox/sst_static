# -*- coding: utf-8 -*-

import nikola.plugin_categories
from nikola.utils import get_logger, STDERR_HANDLER
import csv
from hashlib import md5
import os

from conf import PROJECT_PATH, WEBSITE_PATH

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
        if not os.path.isfile(self.file_in):
            print(f"Users.csv input file not found.  Need to build from Google Drive masters.")
        else:
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

    def add_user(self, user, pswd):
        user_md5 = md5(user.encode('utf-8')).hexdigest()
        pswd_md5 = md5(pswd.encode('utf-8')).hexdigest()
        with open(self.file_out, 'r') as fd_in:
            file_content = fd_in.readlines()
            fd_in.close()
        if 'user_logins' in file_content[0]:   # remove javascript code
            file_content = file_content[1:]
        out_content = []
        for line in file_content:
            if len(line) > 10 and user_md5 not in line:
                out_content.append(line)
        out_content[-1] = out_content[-1].replace("}", ",")
        out_content.append('"' + user_md5 + '": "' + pswd_md5 + '"}')
        with open(self.file_out, 'w') as fd_out:
            fd_out.write("var user_logins = {")
            for line in out_content:
                fd_out.write(line )
            fd_out.close()


    def remove_user(self, user):
        user_md5 = md5(user.encode('utf-8')).hexdigest()
        with open(self.file_out, 'r') as fd_in:
            file_content = fd_in.readlines()
            fd_in.close()
        if 'user_logins' in file_content[0]:   # remove javascript code
            file_content = file_content[1:]
        out_content = []
        for line in file_content:
            if len(line) > 10 and user_md5 not in line:
                out_content.append(line)
        if out_content[-1].endswith(',\n'):
            out_content[-1] = out_content[-1].replace(",", "}")
        with open(self.file_out, 'w') as fd_out:
            fd_out.write("var user_logins = {")
            for line in out_content:
                fd_out.write(line )
            fd_out.close()


converter = MakeUserLogins()


class MakeLogins(nikola.plugin_categories.Command):
    name = 'make_user_logins'
    logger = None
    doc_usage = "[options]"
    doc_purpose = "Make login credential file of users."
    cmd_options = (
        {
            'name': 'function',
            'short': 'f',
            'long': 'function',
            'default': "none",
        },
        {
            'name': 'user',
            'short': 'u',
            'long': 'user',
            'default': "",
            'type': str,
        },
        {
            'name': 'password',
            'short': 'p',
            'long': 'password',
            'default': "Sunny",
            'type': str,
        },
    )

    def __init__(self):
        super(MakeLogins, self).__init__()

    def _execute(self, options, args):
        self.logger = get_logger('ping', STDERR_HANDLER)
        if 'function' in options.keys():
            opt = options['function']
            if 'user' not in options.keys():
                print(f"No user given to add user (or option misspelled).")
                return
            user = options['user']
            if opt in ['a', 'add', 'add_user']:
                if 'password' in options.keys():
                    pswd = options['password']
                else:
                    pswd = converter.default_password
                converter.add_user(user, pswd)
            elif opt in ['r', 'remove', 'delete']:
                converter.remove_user(user)
            else:
                converter.make_logins()
