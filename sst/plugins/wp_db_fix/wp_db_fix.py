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
from conf import PARENT_PATH, PROJECT_PATH, WEBSITE_PATH

class WpDBFix(object):
    def __init__(self):
        self.web_source = WEBSITE_PATH + '/pages'
        self.file_in = PROJECT_PATH + 'support/db.sql'
        self.file_out = PROJECT_PATH + 'support/db_out.sql'

    def close(self):
        pass

    def fix_db(self):
        """The Wordpress database dump creates an invalid load in that it provides a default date where
        none existed in the source.  The default date is of the form '0000-00-00' which is itself invalid for
        MySQL.  This routine simply finds and replaces all instances of that date format with a valid one."""
        with open(self.file_in, 'r') as fd_in:
            with open(self.file_out, 'w+') as fd_out:
                count = 0
                for line in fd_in.readlines():
                    if line.find('0000-00-00') != -1:
                        count += 1
                        line_out = line.replace('0000-00-00', '2000-01-01')
                    else:
                        line_out = line
                    fd_out.writelines(line_out)
                fd_out.close()
            fd_in.close()
        print(f"{count} dates corrected")

    def file_reader(self):
        for line in self.content_dict['fixes']:
            yield line

converter = WpDBFix()


class FixCode(nikola.plugin_categories.Command):
    name = 'wp_db_fix'
    logger = None

    def __init__(self):
        super(FixCode, self).__init__()

    def _execute(self, command, args):
        self.logger = get_logger('ping', STDERR_HANDLER)
        converter.fix_db()
