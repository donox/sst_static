# -*- coding: utf-8 -*-

# A WordPress compiler plugin for Nikola
#
# Copyright (C) 2020 by Don Oxley
# Copyright (C) by the WordPress contributors
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import nikola.plugin_categories
# this is a reference to another package at the same level
from sst.shortcode_processing.ss_shortcode_mgr import ReplaceShortcodes
from nikola.utils import get_logger, STDERR_HANDLER

converter = ReplaceShortcodes()


class Code(nikola.plugin_categories.Command):
    name = 'convert_shortcodes'
    # compiler_name = 'wordpress'
    logger = None

    def __init__(self):
        super(Code, self).__init__()

    def _execute(self, command, args):
        self.logger = get_logger('ping', STDERR_HANDLER)
        converter.clean_image_directories()
        converter.process_pages()
