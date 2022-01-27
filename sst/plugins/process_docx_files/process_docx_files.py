# -*- coding: utf-8 -*-
import subprocess

import nikola.plugin_categories
from nikola.utils import get_logger, STDERR_HANDLER
import os
import shutil
from conf import PARENT_PATH, PROJECT_PATH, WEBSITE_PATH


class DocxProcessor(object):
    def __init__(self):
        self.web_source = WEBSITE_PATH + 'pages'
        self.files_to_process = PROJECT_PATH + 'support/docx_pages'

    def close(self):
        pass

    def process_docx_files(self):
        for os_list in [self.files_to_process]:
            for dirpath, _, fileList in os.walk(os_list):
                for file in fileList:
                    if file.endswith('meta'):       # we look up md file based on meta file
                        in_meta = dirpath + '/' + file
                        with open(in_meta, 'r') as meta:
                            metadata = meta.readlines()
                            meta.close()
                        docx_filename = file[:-4] + 'docx'  # Strip 'meta' and replace with 'docx'
                        in_docx = dirpath + '/' + docx_filename
                        ml_filename = file[:-4] + 'md'
                        in_md = dirpath + '/' + ml_filename
                        save_dir = ''
                        command = ["pandoc", f"{in_docx}", "-o",  f"{in_md}"]
                        try:
                            res = subprocess.run(command, check=True)
                        except Exception as e:
                            print(f'Error running pandoc with command: {command} and error: {e}')
                        # NOTE:  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        # Pandoc is escaping a number of characters including (_, $, ").  We need to correct
                        # only for such characters occurring in the shortcode
                        with open(in_md, 'r') as created_md:
                            md_content = created_md.read()
                            # TODO:  create generator returning just shortcodes and do replace within
                            md_content = md_content.replace("\\_", "_").replace('\\"', '"').replace("\\$", "$")
                            created_md.close()
                        with open(in_md, 'w') as created_md:
                            created_md.write(md_content)
                            created_md.close()
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


converter = DocxProcessor()


class ProcessDocxFiles(nikola.plugin_categories.Command):
    name = 'process_docx_files'
    logger = None

    def __init__(self):
        super(ProcessDocxFiles, self).__init__()

    def _execute(self, command, args):
        self.logger = get_logger('ping', STDERR_HANDLER)
        converter.process_docx_files()
