# -*- coding: utf-8 -*-
import subprocess

import nikola.plugin_categories
from nikola.utils import get_logger, STDERR_HANDLER
import os
import shutil
from conf import PARENT_PATH, PROJECT_PATH, WEBSITE_PATH
from plugins.process_docx_files.flexbox_support import SupportFlexbox
from collections import deque


class DocxProcessor(object):
    def __init__(self):
        self.web_source = WEBSITE_PATH + 'pages'
        self.files_to_process = PROJECT_PATH + 'support/docx_pages'
        self.transl_table = dict([(ord(x), ord(y)) for x, y in zip(u"‘’´“”–-", u"'''\"\"--")])

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
                        command = ["pandoc", f"{in_docx}", "-o",  f"{in_md} -t markdown-simple_tables+pipe_tables "]
                        try:
                            res = subprocess.run(command, check=True)
                        except Exception as e:
                            print(f'Error running pandoc with command: {command} and error: {e}')
                        # NOTE:   !!!!!!!!!!!!!!!!!!!!!!!
                        # Pandoc surrounds each line in a <p></p> element.  This can cause broken html
                        # for any shortcode that spans multiple lines - in particular, those with separate
                        # start and end elements (the box shortcode defends against this).

                        # NOTE:  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        # Pandoc is escaping a number of characters including (_, $, ").  We need to correct
                        # only for such characters occurring in the shortcode

                        # NOTE:  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        # This is a hack as Pandoc appears to be appending the parameter char string to the outfile name
                        file_base = ml_filename.split('.')[0]
                        dir_files = os.listdir(dirpath)
                        for file_nm in dir_files:
                            if file_nm.startswith(file_base):
                                if file_nm.strip().endswith('markdown-simple_tables+pipe_tables'):
                                    # This is the file that has been misnamed
                                    os.rename(dirpath + '/' + file_nm, dirpath + '/' + file_base + '.md')
                        # END OF HACK

                        with open(in_md, 'r') as created_md:
                            md_content = created_md.read()
                            # Replace non-ASCII chars (smart quotes, long dash, ..)
                            md_content = ''.join(md_content).translate(self.transl_table)
                            created_md.close()

                            flex = SupportFlexbox()
                            result = []
                            flex.process_box_shortcodes(md_content, result)
                            revised_content = ''.join(result)

                            # Note: flexbox processing must be completed before removing tags or nikola has a
                            # shortcode error on the /box shortcode.
                            revised_content = self.remove_p_tags(revised_content)
                            revised_content = self.fix_list_items(revised_content)

                        with open(in_md, 'w') as created_md:
                            created_md.write(revised_content)
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

    def remove_p_tags(self, content):
        """Find html p tags immediately surrounding a shortcode and remove them."""
        split_content = content.split('<p>{{%')
        res = []
        for segment in split_content:
            end_code = segment.find('%}}')
            if end_code > -1:
                if segment[end_code:end_code+7] == '%}}</p>':
                    res.append('{{%' + segment[:end_code + 3])
                    if len(segment) > end_code + 8:
                        res.append(segment[end_code+8:])
                else:
                    res.append('<p>{{%' + segment)
            else:
                res.append(segment)
        return ''.join(res)

    def fix_list_items(self, content):
        """Remove p tag from inside a list item inserted by Pandoc"""
        split_content = content.split('<li><p>')
        res = []
        for segment in split_content:
            end_code = segment.find('</p></li>')
            if end_code > -1:
                res.append('<li>' + segment[:end_code] + '</li>' + segment[end_code+9:])
            else:
                res.append(segment)
        return ''.join(res)


converter = DocxProcessor()


class ProcessDocxFiles(nikola.plugin_categories.Command):
    name = 'process_docx_files'
    logger = None

    doc_purpose = "Convert docx files in support/docx_pages to md files in pages."
    doc_usage = "TBD"    # see https://www.getnikola.com/extending.html#command-plugins for example

    def __init__(self):
        super(ProcessDocxFiles, self).__init__()

    def _execute(self, command, args):
        self.logger = get_logger('ping', STDERR_HANDLER)
        converter.process_docx_files()
