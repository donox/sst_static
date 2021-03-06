# -*- coding: utf-8 -*-

import nikola.plugin_categories
from nikola.utils import get_logger, STDERR_HANDLER
import os
import shutil
from conf import PARENT_PATH, PROJECT_PATH, WEBSITE_PATH


class ProcessMigrations(object):
    def __init__(self):
        self.web_source = WEBSITE_PATH + 'pages'
        self.files_to_process = WEBSITE_PATH + 'migrating_pages'
        self.support_files = PROJECT_PATH + 'support/admin_pages'

    def close(self):
        pass

    def process_migrations(self):
        for os_list in [self.files_to_process, self.support_files]:
            for dirpath, _, fileList in os.walk(os_list):
                for file in fileList:
                    if file.endswith('meta'):       # we look up md file based on meta file
                        in_meta = dirpath + '/' + file
                        with open(in_meta, 'r') as meta:
                            metadata = meta.readlines()
                            meta.close()
                        ml_filename = file[:-4] + 'md'
                        in_md = dirpath + '/' + ml_filename
                        save_dir = ''
                        for line in metadata:
                            line_pos = line.find(' path:')
                            if line_pos != -1:
                                save_dir = line[line_pos+6:].strip()
                                if save_dir[0] == '/':
                                    save_dir = save_dir[1:]     # remove any leading slash
                                if save_dir[-1] == '/':
                                    save_dir = save_dir[:-1]     # remove any trailing slash
                                break
                        if save_dir:
                            out_md = WEBSITE_PATH + save_dir + '/' + ml_filename
                            out_meta = WEBSITE_PATH + save_dir + '/' + file
                            try:
                                if not os.path.exists(WEBSITE_PATH + save_dir):
                                    path_tree = save_dir.split('/')
                                    base_path = WEBSITE_PATH
                                    for path_seg in path_tree:
                                        base_path += path_seg + '/'
                                        if not os.path.exists(base_path):
                                            os.mkdir(base_path)
                                shutil.copyfile(in_md, out_md)
                                shutil.copyfile(in_meta, out_meta)
                            except Exception as e:
                                print(f'Error moving file: {file[:-5]} with error: {e}')
                    if file.endswith('yaml'):
                        in_fl = dirpath + '/' + file
                        out_fl = WEBSITE_PATH + 'files/admin/' + file
                        shutil.copyfile(in_fl, out_fl)

converter = ProcessMigrations()


class PageMigrations(nikola.plugin_categories.Command):
    name = 'pages_in_migration'
    logger = None

    def __init__(self):
        super(PageMigrations, self).__init__()

    def _execute(self, command, args):
        self.logger = get_logger('ping', STDERR_HANDLER)
        converter.process_migrations()
