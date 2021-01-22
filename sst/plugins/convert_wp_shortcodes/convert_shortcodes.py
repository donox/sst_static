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
from conf import PARENT_PATH, PROJECT_PATH, WEBSITE_PATH, SITE_URL

import platform

def run_jinja_template(template, context):
    try:
        env = Environment(
            loader=FileSystemLoader(WEBSITE_PATH + 'sc_templates'),
            autoescape=(['html']))
        template = env.get_template(template)
        results = template.render(context)
        return results
    except Exception as e:
        print(e.args)
        raise e


class ReplaceShortcodes(object):
    available_shortcodes = ['maxbutton', 'singlepic', 'src_singlepic', 'ngg_images', 'src_slideshow', 'child-pages']
    unhandled_shortcodes = ['ultimatemember', 'ultimatemember_account', 'wp_google_search', 'srcp_wellness_center',
                            'srcp_wellness_individual', 'srcp_wellness_statistics', 'src_lists_membership',
                            'src_lists_admin_functions', 'catlist', 'sustainability', 'includeme',
                            'thermometer', 'ninja_forms', 'src_manage_opportunity', 'src_record_registration',
                            'src_sign_up_for_opportunity', 'src_list_opportunities', 'src_register_opportunity',
                            'src_create_opportunity', 'src_fwf_notify', 'nggallery', 'ngg', 'srcp_club_membership']
    # We support two flavors of argument list:
    # (1) The value of an individual argument is surrounded by quotes (' or ")
    # (2) The value of an argument is a single character string [a-zA-Z_]
    # -- the argument types may not be mixed.

    # Note that the "^]]" below defends against a left bracket immediately following a shortcode
    sc_re = re.compile(r'\[([a-zA-Z0-9\-_]+) *(\w+=[^\]]+)* *\]', re.I)
    sc_re_arg = re.compile(r'( *([A-Za-z0-9_]+) *= *"(.*)")+?')
    sc_re_arg_no_quotes = re.compile(r'( *([A-Za-z0-9_]+) *= *(.[a-zA-Z_]+))+?')

    sc_re_hard_links = re.compile(r'href=\"(.*?sunnyside-times.com/)')

    def __init__(self):
        self.web_source = WEBSITE_PATH + 'pages'
        self.content_dict = {}
        self.current_file = ''
        self.unhandled = []
        self.button = False
        self.shortcode_string = ''
        self.pic_manager = HandlePictureImports()
        self.pics = self.pic_manager.get_all_pics()
        self.inverse = {}
        self.files = set()
        self.content_dict['bad'] = open(PROJECT_PATH + 'support/bad_urls.txt', 'w')
        self.content_dict['issues'] = open(PROJECT_PATH + 'support/issues.txt', 'w')
        self.content_dict['fixes'] = open(PROJECT_PATH + 'support/fixes.txt', 'w')
        self.dead_files = set()
        with open(PROJECT_PATH + 'support/marked_bad_urls.txt', 'r') as bads:
            not_done = True
            while not_done:
                ln = bads.readline()
                if ln.startswith('???'):
                    file = bads.readline().split('/')[-1]
                    self.dead_files.add(file[:-1])  # Remove trailing \n
                elif ln.startswith('DONE'):
                    not_done = False
        self._build_inverse()

    def close(self):
        if self.content_dict['bad']:
            self.content_dict['bad'].close()
            self.content_dict['bad'] = None
        self.content_dict['issues'].close()
        self.content_dict['fixes'].close()

    def _build_inverse(self):
        # file '.md' is the top level file.  Rename to page-one.md
        page_path = WEBSITE_PATH + '/pages/'
        try:
            os.rename(page_path + '.md', page_path + 'page-one.md')
            os.rename(page_path + '.meta', page_path + 'page-one.meta')
        except:
            pass
        try:
            shutil.rmtree(page_path + 'sandbox')
        except:
            pass
        for dirpath, _, fileList in os.walk(self.web_source):
            for file in fileList:
                if not file.endswith('meta'):
                    if file not in self.files:
                        self.files.add(file)
                        sub_path = dirpath[dirpath.find('pages'):]
                        dir_parts = sub_path.split('/')
                        self.inverse[file] = dir_parts
                    else:
                        self.content_dict['issues'].writelines(f'Duplicate file: {file}\n\n')

    def clean_image_directories(self):
        """remove wp directories from image folders"""
        self.pic_manager.remove_unnecessary_wp_folders()

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
                        not dirpath.endswith('-notes'):  #   and \
                        # fname != 'the-daffodil-man.md':
                        # not fname.startswith('veteran') and \
                        # fname == 'page-one.md':
                    file_path = os.path.join(dirpath, fname)
                    self.content_dict['file_path'] = file_path
                    # print(file_path)
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        self.current_file = file_path
                        self.shortcode_string = ''.join(infile.readlines())
                        current_string = self.parse_a_tag(self.shortcode_string)
                        current_string = self.parse_hard_links(current_string)
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

    def parse_shortcode(self, shortcode_string):
        """Find the first shortcode in a string. """
        # Does not handle case where shortcode has contained string "[xx] yy [/xx]"
        if not shortcode_string:
            return None
        # print(shortcode_string)
        matches = re.search(ReplaceShortcodes.sc_re, shortcode_string)
        if matches is None or matches.groups() is None:
            # print("No shortcodes found")
            return
        res = dict()
        for n, match_group in enumerate(matches.groups()):
            if not n:  # detecting first group which is the shortcode identifier
                res['shortcode'] = match_group.lower()
                res['full code'] = shortcode_string[matches.start():matches.end()]
                res['start'] = matches.start()
                res['end'] = matches.end()
                if res['shortcode'] in ReplaceShortcodes.unhandled_shortcodes:
                    self.content_dict['issues'].writelines(
                        f"UNHANDLED SHORTCODE: in: {self.content_dict['file_path']} is: {self.shortcode_string[:100]}++\n\n")
                    return res
                if res['shortcode'] not in ReplaceShortcodes.available_shortcodes:
                    self.content_dict['issues'].writelines(
                        f"UNRECOGNIZED SHORTCODE: in: {self.content_dict['file_path']} is: {self.shortcode_string[:100]}++\n\n")
                    return res
            if match_group:
                try:
                    # print("n: {}, {}".format(n, match))
                    if n > 0:
                        arg_list = match_group
                        max_loop_count = 20
                        while len(
                                arg_list) > 0 and max_loop_count > 0:  # Use max_loop_count to defend against infinite loop
                            try:
                                parm1, parm2, arg_list = self._get_next_arg(arg_list, ReplaceShortcodes.sc_re_arg)
                                res[parm1.lower()] = parm2
                                max_loop_count -= 1
                            except:
                                return "SHORTCODE ARG FAILURE"
                except:
                    print("No Match on {}".format(n))
        # self.content_dict = res               # ########WHY DO THIS
        return res

    def _get_next_arg(self, arg_string, arg_re):
        work_temp = arg_string.strip()
        if work_temp == '':
            return None

        eq_loc = str.find(work_temp, '=')
        if eq_loc == -1:
            return None
        if str.find(work_temp[eq_loc:], '"') == -1:
            foo = 3
        name = work_temp[0:eq_loc]
        name = name.strip()
        start_arg_loc = str.find(work_temp[eq_loc:], '"') + eq_loc + 1
        end_arg_loc = str.find(work_temp[start_arg_loc:], '"')
        end_arg_pos = start_arg_loc + end_arg_loc
        arg = work_temp[start_arg_loc: end_arg_pos]
        rem = work_temp[end_arg_pos + 1:]
        return name, arg, rem

    def _get_parm_list(self, parm, expected_type):
        if parm in self.content_dict.keys():
            parm_list = self.content_dict[parm].split(',')
            try:
                return [expected_type(x) for x in parm_list]
            except TypeError as e:
                raise ValueError('Conversion Failure: {} is not of type {}'.format(parm_list, str(expected_type)))

    def _process_shortcode(self, shortcode_content):
        sc = shortcode_content['shortcode']
        if sc == 'maxbutton':
            return self._process_maxbutton(shortcode_content)
        elif sc == 'singlepic' or sc == 'src_singlepic':
            res = self._process_singlepic(shortcode_content)
            return res
        elif sc == 'src_slideshow' or sc == 'ngg_images':
            res = self._process_slideshow(shortcode_content)
            return res
        elif sc == 'child-pages':
            # The real work occurs in the actual shortcode processor during build
            # handling it here allows for use by end users after transition to Nikola is complete
            # while still processing child_link codes from WP
            res = '{{% build_links_to_children %}}'
            return res
        else:
            if sc not in self.unhandled:
                self.unhandled.append(sc)
            return shortcode_content['full code']

    def _process_slideshow(self, show_content):
        all_keys = show_content.keys()
        if 'ids' in all_keys:
            key = 'ids'
        elif 'image_ids' in all_keys:
            key = 'image_ids'
        else:
            # raise ValueError(f"Slideshow with non-standard id list in file: {self.current_file}")
            return 'PARSE FAILURE'
            # raise ValueError(f'No id key found in {show_content}')
        try:
            pic_ids = [int(x.strip()) for x in show_content[key].split(',') if x != '']
            if len(pic_ids) == 1:
                self.content_dict['fixes'].writelines(f"One pic slideshow: {self.current_file}\n")
        except ValueError as e:
            fn = self.content_dict['file_path']
            self.content_dict['issues'].writelines(f"Non-digit ID in list: {show_content[key]} for file: {fn}")
            return 'PARSE FAILURE'
        # Make a (probably) unique gallery id by multiplying the pic ids modulo 10K
        gallery_name = f'Gal{reduce(mul, pic_ids) % 100000}'
        gal_path = WEBSITE_PATH + 'galleries/' + gallery_name
        if os.path.exists(gal_path):
            return  # Presume if it exists, that it is the same as we are creating
        else:
            os.mkdir(gal_path)
            x_pic_ids = list(set(pic_ids))  # Eliminate duplicates in list (may lose order)
            for pic_id in x_pic_ids:
                ws = WEBSITE_PATH[:-1]
                pick_path = self.pic_manager.get_path_for_pic_id(pic_id)
                if not pick_path:
                    fn = self.content_dict['file_path']
                    self.content_dict['issues'].writelines(f"No Path found for picture id: {pic_id} in file: {fn}\n\n")
                    return 'PARSE FAILURE'
                else:
                    pick_path = ws + pick_path
                if not os.path.exists(pick_path):
                    self.content_dict['issues'].writelines(
                        f"PICTURE: {pick_path} IS MISSING IN FILE: {self.content_dict['file_path']}\n\n")
                    pick_path = ''
                    pic_ids = [x for x in pic_ids if x != pic_id]
                else:
                    shutil.copy(pick_path, gal_path)
            if pic_ids:
                with open(gal_path + '/metadata.yml', 'w') as yml:
                    for n, pic_id in enumerate(x_pic_ids):
                        # names=['pid', 'filename', 'alttext', 'imagedate', 'caption', 'path'])
                        caption = self.pics.caption.loc[pic_id]
                        if isinstance(caption, float):  # some captions show up as nan
                            caption = ''
                        if caption.find(':') != -1:
                            caption = caption.replace(':', ',')     # Can't have ':' or ';' in captions apparently
                        file_name = self.pics.filename.loc[pic_id]
                        yml.writelines('---\n')
                        yml.writelines(f"name: {file_name}\n")
                        if caption:
                            yml.writelines(f"caption: {caption}\n")
                        yml.writelines(f"order: {n}\n")
                        if not n:  # Can't have separate section that is not tied to an image :-(
                            yml.writelines(
                                f"Gallery source page: '{self.content_dict['file_path']} with gallery name - {gallery_name}'\n")
                    yml.writelines('---\n')
                    yml.close()
            shortcode = '{{% gallery ' + gallery_name + ' %}}'
        return shortcode

    def _process_maxbutton(self, button_content):
        try:
            button_type = button_content['id']
            if 'text' in button_content.keys():
                text_content = button_content['text']
                if text_content.startswith('Read'):
                    foo = 3
            else:
                # TODO: WHere does 'window' come from?  What is going on here?
                if 'window' in list(button_content.keys()):
                    text_content = button_content['window']
                else:
                    text_content = "No Button Text"
            url_content = button_content['url']
        except KeyError as e:
            print("Maxbutton Key Error in dict: {}".format(button_content))
            raise e
        try:
            target_page = self._adjust_url(url_content)
            if not target_page:
                self._adjust_url(url_content)  # RETRY FOR DEBUGGING
                res = f'URL: {url_content} does not exist or is malformed.'
                return res
            # TODO:  Does this handle a url that is a download properly???????????????????????????//
        except Exception as e:  # some urls seem to be bad
            self.content_dict['bad'].writelines(f'URL: {url_content}\n\tFILE: {self.content_dict["file_path"]}\n\n')
            return None
        button_type = "is-link"
        context_dict = {'button_type': button_type,
                        'extra_styling': 'margin:3px;',
                        'target': target_page,
                        'text_content': text_content}
        context = {'button': context_dict}
        res = run_jinja_template('/base/button.jinja2', context=context).replace('\n', '')
        return res

    def _adjust_url(self, url):
        """Convert url from Wordpress MaxButton to Nikola site."""
        parsed_url = urlparse(url)
        if not parsed_url.hostname:
            is_ss_absolute = False
        else:
            is_ss_absolute = parsed_url.hostname.find('sunnyside-times') != -1
        if parsed_url.hostname and not is_ss_absolute:
            return url
        try:
            source_file_parts = self.content_dict['file_path'].split('/')
        except Exception as e:
            raise ValueError(f'Invalid file_path to split: {self.content_dict["file_path"]}')
        tmp_down = url.find('downloads')
        if tmp_down != -1:
            down_url = url[tmp_down:]
            nbr_double_period = len(source_file_parts) - source_file_parts.index('pages')
            lead = '../' * nbr_double_period
            res = lead + down_url
            return res
        url_parts = url.split('/')
        if url_parts[-1] == '':
            url_parts = url_parts[:-1]
        file_name = url_parts[-1] + '.md'
        try:
            file_parts = self.inverse[file_name]
        except Exception as e:
            self.content_dict['bad'].writelines(f'Unrecognized URL: {url} in {self.content_dict["file_path"]}\n\n')
        nbr_double_period = len(source_file_parts) - source_file_parts.index('pages')
        lead = '../' * nbr_double_period
        res = lead + '/'.join(file_parts) + '/' + url_parts[-1]
        return res

    def _process_singlepic(self, pic_content):
        try:
            if 'id' in pic_content.keys():
                pic_id = pic_content['id']
                if pic_id.isdigit():
                    pic_path = self.pic_manager.get_path_for_pic_id(int(pic_id))
                    if not pic_path:
                        self.content_dict['issues'].writelines(
                            f'NO PATH FOUND FOR:  {pic_id} with shortcode: {self.shortcode_string[:100]}++\n\n')
                        pic_path = ''
                else:
                    pic_path = ''
                    self.content_dict['issues'].writelines(
                        f'INVALID PICTURE ID: {pic_id} with shortcode: {self.shortcode_string[:100]}++\n\n')
            else:
                raise ValueError(f'Missing pic ID in {pic_content["shortcode"]}')
            if 'w' in pic_content.keys():
                width = pic_content['w'] + 'px'
            else:
                width = '300px'  # TODO: parameterize in conf.py
            if 'h' in pic_content.keys():
                height = pic_content['h'] + 'px'
            else:
                height = '300px'
            if 'float' in pic_content.keys():
                float_pic = pic_content['float']
            else:
                float_pic = 'right'
            if 'caption' in pic_content.keys():
                caption = pic_content['caption']
                if caption == 'nan':
                    caption = ''
            else:
                caption = ''
            if 'title' in pic_content.keys():
                title = pic_content['title']
                if caption == 'nan':
                    title = ''
            else:
                title = ''
            try:
                res = '{{% singlepic image="' + pic_path + '" width="' + width + '" height="' + height + '" '
                res += 'alignment="' + float_pic + '" caption="' + caption + '"' + ' title="' + title + '"'
                res += ' %}}'
            except Exception as e:
                raise ValueError(f"Error: {e} generating singlepic shortcode with content: {pic_content} ")
            # photo = {'url': pic_path,
            #          'width': width,
            #          'height': height,
            #          'alignment': float_pic,
            #          'caption': caption
            #          }
            # context = {'photo': photo}
            # res = run_jinja_template('/base/picture_base.jinja2', context=context)
            # res = " ".join(res.split())
            return res

        except KeyError as e:
            print("Singlepic Key Error in dict content: {}".format(pic_content))
            raise e

    def parse_a_tag(self, file_string):
        """Parse 'a' tags updating href's."""
        # <a href="%5Burl%5D/wp-content/downloads/TandT%20Archive/201806.pdf" target="_blank">June2018</a>
        re_finder = re.compile(r'(<a.+href=\"(.+?)\".*</a>)')
        a_tags = re.finditer(re_finder, file_string)
        string_start = 0
        string_res = ''
        tag_count = -1
        for a_count, a_tag in enumerate(a_tags):
            tag_count = a_count
            begin_a_ref = a_tag.start(2)
            string_res += file_string[string_start:begin_a_ref]
            end_a_ref = a_tag.end(2)
            a_ref = a_tag.group(2)
            has_download = a_ref.find('ownloads')
            if has_download != -1:
                has_download -= 1
                a_ref = a_ref[has_download:]
                source_file_parts = self.content_dict['file_path'].split('/')
                nbr_double_period = len(source_file_parts)      # determine nesting in wp url
                # lead = '../' * nbr_double_period
                lead = ''         # THIS DOES  NOTHING - is there a missing case???
                a_ref = '/' + lead + a_ref
            else:
                pass
            string_res += a_ref
            string_start = end_a_ref
        if tag_count != -1:
            string_res += file_string[string_start:]
            return string_res
        return file_string
    
    def parse_hard_links(self, file_string):
        """Look for instances of hard links with sunnyside-times.com and fix"""
        hard_links = re.finditer(ReplaceShortcodes.sc_re_hard_links, file_string)
        site = '/'.join(SITE_URL.split('/')[:-2])  + '/pages/'     # remove site name from URL as it is supplied on reference
        string_start = 0
        string_res = ''
        tag_count = -1
        for link_count, hard_link in enumerate(hard_links):
            tag_count = link_count
            begin_a_ref = hard_link.start(1)
            string_res += file_string[string_start:begin_a_ref]
            end_a_ref = hard_link.end(1)
            string_res += site
            string_start = end_a_ref
        if tag_count != -1:
            string_res += file_string[string_start:]
            return string_res
        return file_string


import pandas as pd


# TO CREATE DATA for self.pics DataFrame:
#   (1) Download WP database and fix default dates
#       sed -i 's/0000-00-00/2000-01-01/' /home/don/Downloads/db.sql
#   (2) Extract csv (/files/pics.csv)
#       select t1.pid, t1.filename, t1.alttext, t1.imagedate, t1.description, t2.path from wp_ngg_pictures as t1
#           join wp_ngg_gallery as t2 on t1.galleryid = t2.gid order by  t1.pid;


class HandlePictureImports(object):
    def __init__(self):
        self.run_jinja_template = None
        self.web_source = WEBSITE_PATH + 'images'
        self.pics = pd.read_csv(''.join([os.getcwd(), '/files/pics.csv']),
                                names=['pid', 'filename', 'alttext', 'imagedate', 'caption', 'path'])
        self.pics.path = self.pics.path.apply(lambda x: x.replace('/wp-content/gallery/', ''))
        self.pics.path = self.pics.path.apply(lambda x: x.replace('wp-content/gallery/', ''))
        self.pics.set_index('pid', inplace=True)

    def set_jinja(self, jinja_proc):
        # Avoid circular import, let shortcode manager pass function
        self.run_jinja_template = jinja_proc

    def remove_unnecessary_wp_folders(self):
        for dirpath, _, _ in os.walk(self.web_source):
            last_segment = os.path.split(dirpath)[1]
            if last_segment in ['cache', 'dynamic', 'thumbs']:
                shutil.rmtree(dirpath)

    def get_path_for_pic_id(self, pic_id):
        if pic_id in self.pics.index:
            path_dir = self.pics.path.loc[pic_id]
            if not path_dir:
                raise ValueError(f'No directory for picture {pic_id}')
            elif path_dir[-1] != '/':
                path_dir += '/'
            return '/images/' + path_dir + self.pics.filename.loc[pic_id]
        else:
            return None  # TODO: Create valid file path indicating non-existent pic

    def get_all_pics(self):
        return self.pics


converter = ReplaceShortcodes()


class ShortcodeConverter(nikola.plugin_categories.Command):
    name = 'convert_shortcodes'
    # compiler_name = 'wordpress'
    logger = None

    def __init__(self):
        super(ShortcodeConverter, self).__init__()

    def _execute(self, command, args):
        self.logger = get_logger('ping', STDERR_HANDLER)
        converter.clean_image_directories()
        converter.process_pages()
