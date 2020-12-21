import re
import os
from urllib.parse import urlparse
from sst.conf import *
from jinja2 import Environment, FileSystemLoader, select_autoescape
from .ss_pics import HandlePictureImports
import shutil
from sst import THIS_PATH


def run_jinja_template(template, context):
    try:
        env = Environment(
            loader=FileSystemLoader(THIS_PATH + 'sst_static/sst/shortcode_processing/sc_templates'),
            autoescape=(['html']))
        template = env.get_template(template)
        results = template.render(context)
        return results
    except Exception as e:
        print(e.args)
        raise e


class ReplaceShortcodes(object):
    # available_shortcodes = ['maxbutton', 'singlepic', 'src_singlepic', 'includeme', 'ngg_images']
    available_shortcodes = ['maxbutton', 'singlepic', 'src_singlepic', ]
    # We support two flavors of argument list:
    # (1) The value of an individual argument is surrounded by quotes (' or ")
    # (2) The value of an argument is a single character string [a-zA-Z_]
    # -- the argument types may not be mixed.

    # Note that the "^]]" below defends against a left bracket immediatelyfollowing a shortcode
    sc_re = re.compile(r'\[(\w+) *(\w+=[^\]]+)* *\]', re.I)
    sc_re_arg = re.compile(r'( *([A-Za-z0-9_]+) *= *"(.*)")+?')
    sc_re_arg_no_quotes = re.compile(r'( *([A-Za-z0-9_]+) *= *(.[a-zA-Z_]+))+?')

    def __init__(self):
        self.web_source = '../sst/pages'
        self.content_dict = {}
        self.unhandled = []
        self.button = False
        self.shortcode_string = ''
        self.pic_manager = HandlePictureImports()
        self.inverse = {}
        self.files = set()
        self._build_inverse()
        self.content_dict['bad'] = open('/home/don/Documents/bad_urls.txt', 'w')
        self.dead_files = set()
        with open('/home/don/Documents/marked_bad_urls.txt', 'r') as bads:
            not_done = True
            while not_done:
                ln = bads.readline()
                if ln.startswith('???'):
                    file = bads.readline().split('/')[-1]
                    self.dead_files.add(file[:-1])  # Remove trailing \n
                elif ln.startswith('DONE'):
                    not_done = False

    def close(self):
        if self.content_dict['bad']:
            self.content_dict['bad'].close()
            self.content_dict['bad'] = None

    def _build_inverse(self):
        # file '.md' is the top level file.  Rename to page-one.md
        page_path = THIS_PATH + 'nikola/sst/pages/'
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
                        print(f'Duplicate file: {file}')

    def clean_image_directories(self):
        """remove wp directories from image folders"""
        self.pic_manager.remove_unnecessary_wp_folders()

    def process_pages(self):
        for dirpath, _, fileList in os.walk(self.web_source):
            # print('Process directory: %s' % dirpath)
            for fname in fileList:
                if fname not in self.dead_files and \
                        fname.endswith('.md') and \
                        not fname.startswith('veteran') and \
                        not dirpath.endswith('-notes'):
                    file_path = os.path.join(dirpath, fname)
                    self.content_dict['file_path'] = file_path
                    # print(file_path)
                    with open(file_path, 'r') as infile:
                        self.shortcode_string = ''.join(infile.readlines())
                        current_string = self.parse_a_tag(self.shortcode_string)
                        result_string = ''
                        while current_string:
                            res = self.parse_shortcode(current_string)
                            if res == 'SHORTCODE ARG FAILURE':
                                print(f'Shortcode failure in: {file_path}')
                                current_string = ''
                            elif res:
                                if res['start']:
                                    # if start is not at front of string, add start of string to result
                                    result_string += current_string[:res['start']]
                                current_string = current_string[res['end']:]
                                self.content_dict['count_slash'] = file_path.count(
                                    '/')  # get path depth for relative reference
                                tmp = self._process_shortcode(res)
                                if tmp:
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
            if match_group == 'singlepic':
                foo = 3
            if not n:  # detecting first group which is the shortcode identifier
                res['shortcode'] = match_group.lower()
                res['full code'] = shortcode_string[matches.start():matches.end()]
                if res['shortcode'] not in ReplaceShortcodes.available_shortcodes:
                    return
            if match_group:
                res['start'] = matches.start()
                res['end'] = matches.end()
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
        else:
            if sc not in self.unhandled:
                self.unhandled.append(sc)
            return shortcode_content['full code']

    def _process_maxbutton(self, button_content):
        try:
            button_type = button_content['id']
            if 'text' in button_content.keys():
                text_content = button_content['text']
                if text_content.startswith('Read'):
                    foo = 3
            else:
                text_content = button_content['window']
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
            self.content_dict['bad'].writelines(f'URL: {url_content}\n\tFILE: {self.content_dict["file_path"]}\n')
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
            self.content_dict['bad'].writelines(f'Unrecognized URL: {url} in {self.content_dict["file_path"]}\n')
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
                else:
                    pic_path = ''
                    print(f'INVALID PICTURE ID: {pic_id} with shortcode: {self.shortcode_string}')
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
            photo = {'url': pic_path,
                     'width': width,
                     'height': height,
                     'alignment': float_pic,
                     'caption': caption
                     }
            context = {'photo': photo}
            res = run_jinja_template('/base/picture_base.jinja2', context=context)
            res = " ".join(res.split())
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
        tag_count = 0
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
                nbr_double_period = len(source_file_parts)
                # lead = '../' * nbr_double_period
                lead = ''
                a_ref = '/' + lead + a_ref
            else:
                pass
            string_res += a_ref
            string_start = end_a_ref
        if tag_count:
            string_res += file_string[string_start:]
            return string_res
        return file_string


# class Shortcode(object):
#     """Handler for a single shortcode.
#
#     """
#     available_shortcodes = ['maxbutton', 'singlepic', 'src_singlepic', 'includeme', 'ngg_images']
#     sc_re = re.compile(r'\[(\w+)( *.+)* *\]', re.I)
#     sc_re_arg = re.compile(r'( *([A-Za-z0-9_]+) *= *"(.*)")+?')
#
#     def __init__(self, db_exec, string_to_match=None):
#         self.db_exec = db_exec
#         self.specific_processors = {'maxbutton': self._process_maxbutton,
#                                     'singlepic': self._process_singlepic,
#                                     'src_singlepic': self._process_singlepic,
#                                     'ngg_images': self._process_ngg_images,
#                                     'includeme': self._process_include_me,
#                                     'caption': None,  # see 'steve-and-david'  not sure where it comes from
#                                     'src_lists_membership': None,
#                                     'src_lists_admin': None
#                                     }
#         self.picture_processors = {'singlepic': self._process_findpic,
#                                     'src_singlepic': self._process_findpic,
#                                     'ngg_images': self._process_ngg_findpics,
#                                     }
#         self.shortcode_string = string_to_match
#         self.content_dict = None
#         self.page_mgr = db_exec.create_page_manager()
#         self.photo_mgr = db_exec.create_sst_photo_manager()
#
#     def parse_shortcode(self):
#         # Does not handle case where shortcode has contained string "[xx] yy [/xx]"
#         if not self.shortcode_string:
#             return None
#         matches = re.search(Shortcode.sc_re, self.shortcode_string)
#         if matches is None or matches.groups() is None:
#             raise ShortcodeSystemError('RE failed to match a shortcode.')
#         res = dict()
#         for n, match in enumerate(matches.groups()):
#             if not n:
#                 res['shortcode'] = match.title().lower()
#             if match:
#                 try:
#                     # print("n: {}, {}".format(n, match.title()))
#                     if n > 0:
#                         arg_list = match.title()
#                         loop_count = 50
#                         while len(arg_list) > 0 and loop_count:         # Use loop_count to defend against infinite loop
#                             try:
#                                 parm1, parm2, arg_list = self._get_next_arg(arg_list)
#                                 res[parm1.lower()] = parm2
#                                 loop_count -= 1
#                             except:
#                                 print("No match arg on {}".format(arg_list))
#                 except:
#                     print("No Match on {}".format(n))
#         self.content_dict = res
#         return res
#
#     def _get_next_arg(self, arg_string):
#         work = arg_string.strip()
#         if work == '':
#             return None
#         eq_loc = str.find(work, '=')
#         if eq_loc == -1:
#             return None
#         name = work[0:eq_loc]
#         name = name.strip()
#         st_arg_loc = str.find(work[eq_loc:], '"') + eq_loc + 1
#         end_arg_loc = str.find(work[st_arg_loc:], '"')
#         end_arg_pos = st_arg_loc + end_arg_loc
#         arg = work[st_arg_loc: end_arg_pos]
#         rem = work[end_arg_pos + 1:]
#         return name, arg, rem
#
#     def _get_parm_list(self, parm, expected_type):
#         if parm in self.content_dict.keys():
#             parm_list = self.content_dict[parm].split(',')
#             try:
#                 return [expected_type(x) for x in parm_list]
#             except TypeError as e:
#                 raise ShortcodeParameterError('Conversion Failure: {} is not of type {}'.format(parm_list,
#                                                                                                 str(expected_type)))
#
#     def process_shortcode(self, pictures_only=False):
#         if not self.content_dict:
#             return None
#         sc = self.content_dict['shortcode']
#         if not pictures_only:
#             if sc in self.specific_processors.keys():
#                 handler = self.specific_processors[sc]
#                 if handler:
#                     handler()
#         else:
#             if sc in self.picture_processors.keys():
#                 handler = self.picture_processors[sc]
#                 if handler:
#                     return handler()
#
#     def _process_findpic(self):
#         """Find photo id for relating photo to page"""
#         photo_id = self.content_dict['id']
#         if type(photo_id) is str:
#             photo_id = int(photo_id)
#         photo_id = self.photo_mgr.get_new_photo_id_from_old(photo_id)
#         return [photo_id]
#
#     def _process_ngg_findpics(self):
#         """Find photo id's for relating photo to page"""
#         keys = self.content_dict.keys()
#         photo_ids = None
#         if 'source' in keys:
#             source = self.content_dict['source']
#             if source.lower() == 'galleries':
#                 ids = self._get_parm_list('container_ids', int)
#                 photo_ids = set()
#                 for p_id in ids:
#                     p_list = self._get_photo_list_by_gallery_id(p_id, old_id=True)
#                     photo_ids = photo_ids.union(set(p_list))
#             else:
#                 raise ShortcodeParameterError("{} is an invalid source for ngg_images".format(source))
#         elif 'gallery_ids' in keys:
#             ids = self._get_parm_list('gallery_ids', int)
#             photo_ids = set()
#             for p_id in ids:
#                 p_list = self._get_photo_list_by_gallery_id(p_id, old_id=True)
#                 photo_ids = photo_ids.union(set(p_list))
#         elif 'image_ids' in keys:
#             photo_ids = self._get_parm_list('image_ids', int)
#         return list(photo_ids)
#
#     def _process_maxbutton(self):
#         try:
#             button_type = self.content_dict['id']
#             text_content = self.content_dict['text']
#             url_content = self.content_dict['url']
#         except KeyError as e:
#             print("Maxbutton Key Error in dict: {}".format(self.content_dict))
#             raise e
#         try:
#             target_page = find_page_from_url(self.db_exec, url_content)
#             if target_page:
#                 page_id = target_page.id
#                 target = 'http://' + Config.SERVER_NAME + "/main/page/" + str(page_id)
#             else:
#                 target = find_download_from_url(url_content)
#                 if not target:
#                     return None  # TODO:  Is this really an error?  Displays as text content of shortcode
#         except Exception as e:  # some urls seem to be bad
#             print(f'Error in Maxbutton URL: {url_content}')
#             return None
#         button_type = "is-link"
#         context_dict = {'button_type': button_type,
#                         'extra_styling': 'margin:3px;',
#                         'target': target,
#                         'text_content': text_content}
#         context = {'button': context_dict}
#         res = run_jinja_template('base/button.jinja2', context=context).replace('\n', '')
#         self.content_dict['result'] = res
#
#     def _get_photo_list_by_gallery_id(self, gallery_id, old_id=False):
#         photo_ids = self.photo_mgr.get_photo_ids_in_gallery_with_id(gallery_id, old_id=old_id)
#         return photo_ids
#
#     def _process_singlepic(self):
#         try:
#             photo_id = self.content_dict['id']
#             if not photo_id:
#                 sst_syslog.make_error_entry(f'No photo ID to _process_singlepic')
#                 return None
#             if type(photo_id) is str:
#                 photo_id = int(photo_id)
#             photo_id = self.photo_mgr.get_new_photo_id_from_old(photo_id)
#             photoframe = SlideShow('NO NAME', self.db_exec)
#             photoframe.add_photo(photo_id)
#             if 'h' in self.content_dict:
#                 photoframe.set_dimension('height', self.content_dict['h'])
#             if 'w' in self.content_dict:
#                 photoframe.set_dimension('width', self.content_dict['w'])
#             if 'title' in self.content_dict:
#                 photoframe.add_title(self.content_dict['title'])
#             if 'align' in self.content_dict:
#                 photo_position = self.content_dict['align']
#                 if photo_position not in ['left', 'middle', 'right', 'top', 'bottom']:
#                     sst_syslog.make_error_entry(f'Unknown photo position: {photo_position}')
#                     photo_position = 'middle'
#                 photoframe.set_position(photo_position)
#             res = photoframe.get_html()
#             self.content_dict['result'] = res
#         except Exception as e:
#             # Capture error, but don't raise exception to avoid returning exception to end user
#             sst_syslog.make_error_entry(f'Error occurred in _process_single_pic {e.args}')
#
#     def _process_ngg_images(self):
#         """Process Imagely shortcode ngg_images with relevant parameters."""
#         # [ngg_images source = "galleries"
#         # container_ids = "155"
#         # display_type = "photocrati-nextgen_pro_slideshow"
#         # image_crop = "1"
#         # image_pan = "1"
#         # show_playback_controls = "0"
#         # show_captions = "1"
#         # caption_class = "caption_overlay_bottom"
#         # caption_height = "50"
#         # aspect_ratio = "first_image"
#         # width = "350"
#         # width_unit = "px"
#         # transition = "fade"
#         # transition_speed = "1"
#         # slideshow_speed = "5"
#         # border_size = "0"
#         # border_color = "#ffffff"
#         # ngg_triggers_display = "always"
#         # order_by = "imagedate"
#         # order_direction = "ASC"
#         # returns = "included"
#         # maximum_entity_count = "500"]
#         try:
#             keys = self.content_dict.keys()
#             if 'source' in keys:
#                 source = self.content_dict['source']
#                 if source.lower() == 'galleries':
#                     ids = self._get_parm_list('container_ids', int)
#                     photo_ids = set()
#                     for p_id in ids:
#                         p_list = self._get_photo_list_by_gallery_id(p_id, old_id=True)
#                         photo_ids = photo_ids.union(set(p_list))
#                 else:
#                     raise ShortcodeParameterError("{} is an invalid source for ngg_images".format(source))
#             elif 'gallery_ids' in keys:
#                 ids = self._get_parm_list('gallery_ids', int)
#                 photo_ids = set()
#                 for p_id in ids:
#                     p_list = self._get_photo_list_by_gallery_id(p_id, old_id=True)
#                     photo_ids = photo_ids.union(set(p_list))
#             elif 'image_ids' in keys:
#                 photo_ids = self._get_parm_list('image_ids', int)
#             width = 0
#             if 'width' in keys:
#                 width = int(self.content_dict['width'])
#             if len(photo_ids) == 0:
#                 raise ShortcodeParameterError("No photo ids detected in shortcode")
#             self.content_dict['photo_list'] = {}
#             if len(photo_ids) == 1:
#                 for photo_id in photo_ids:  # retrieve single element from either list or set
#                     break
#             photoframe = SlideShow(None, self.db_exec)
#             for p_id in photo_ids:
#                 photoframe.add_photo(p_id)
#             if 'h' in keys:
#                 photoframe.set_dimension('height', self.content_dict['h'])
#             if 'w' in keys:
#                 photoframe.set_dimension('width', self.content_dict['w'])
#             if 'title' in keys:
#                 photoframe.add_title(self.content_dict['title'])
#             if 'align' in keys:
#                 photo_position = self.content_dict['align']
#                 if photo_position not in ['left', 'middle', 'right', 'top', 'bottom']:
#                     raise ValueError(
#                         'Unknown photo position: {}'.format(photo_position))  # TODO: return error to script
#                 photoframe.set_position(photo_position)
#             res = photoframe.get_html()
#             self.content_dict['result'] = res
#
#         except ShortcodeError as e:
#             raise e
#
#     def _process_include_me(self):
#         """Process 'includeme' shortcode.
#             Example: [includeme file="wp-content/gen-pagesXX/resident_stories.html"]
#         """
#         try:
#             file = self.content_dict['file'].lower()
#         except KeyError as e:
#             print("Maxbutton Key Error in dict: {}".format(self.content_dict))
#             raise e
#         self.content_dict['result'] = 'Error processing shortcode includeme for file: {}'.format(file)
#         file_parts = file.split('/')
#         if file_parts[0] == 'wp-content':
#             file_parts = file_parts[1:]
#         if file_parts == [] or file_parts[0] not in ['downloads', 'gen-pagesXX', 'plots', 'uploads']:
#             raise ShortcodeParameterError('Included file not in expected directory: {}'.format(file))
#         file = Config.USER_DIRECTORY_BASE + '/'.join(file_parts)
#
#         with open(file, 'r') as fl:
#             res = fl.read()
#             fl.close()
#         if res:
#             self.content_dict['result'] = '<div>' + res + '</div>'
