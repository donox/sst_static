# -*- coding: utf-8 -*-
import os
import re

from nikola.plugin_categories import ShortcodePlugin
from nikola.utils import get_logger, STDERR_HANDLER
import nikola.plugin_categories
from conf import PROJECT_PATH, WEBSITE_PATH
from jinja2 import Environment, FileSystemLoader
from utilities.meta_files import make_meta_file_content
import config_private as pvt
import shutil


class PhotoUsage(object):
    # This command creates admin pages showing photos in use and where they are used
    # along with photos (or galleries) no longer in use.

    gal_re = r'{{% +(gallery) +([a-zA-Z0-9\-_]+) +?%}}'
    pic_re = r'{{% +(singlepic) image=\"([a-zA-Z0-9_\-\/\.]+)\" .*?%}}'
    photo_re = re.compile(gal_re + '|' + pic_re)

    def __init__(self):
        self.site = None
        self.galleries_dir = PROJECT_PATH + 'sst/galleries'
        self.images_dir = PROJECT_PATH + 'sst/images'
        self.pages_dir = PROJECT_PATH + 'sst/pages'
        self.outfiles_dir = PROJECT_PATH + 'sst/pages/admin'
        # Both dictionaries keyed with path (below sst)
        self.photos = dict()
        self.pages = dict()
        self.galleries = dict()
        self.images_in_a_page = set()
        self.image_list = set()
        self.image_names = set()   # image names independent of folder
        self.galleries_in_a_page = set()
        self.images_in_galleries = set()
        self.gallery_list = set()
        self.unused_images = set()
        self.unused_galleries = set()

    def handler(self, *args, **kwargs):
        # Build context for creating display pages with jinja templates
        context = {'all_pages': self.pages, 'all_photos': self.photos, 'all_galleries': self.galleries,}
        # Create list of images with name and path for each
        for root, dirs, files in os.walk(self.images_dir):
            short_path = root.split('/sst/')[1]
            for file in files:
                self.image_list.add('/' + short_path + '/' + file)
                self.image_names.add(file)
                if file not in self.photos:
                    self.photos[file] = []
                photo_ref = dict()
                photo_ref["path"] = short_path
                photo_ref["file"] = file
                photo_ref["in_gallery"] = False
                self.photos[file].append(photo_ref)
        # Create list giving images in each gallery
        for root, dirs, files in os.walk(self.galleries_dir):
            for a_dir in dirs:
                gal_path = os.path.join(root, a_dir)
                short_gal_path = gal_path.split('/sst/')[1]
                self.gallery_list.add(a_dir)
                for file in os.listdir(gal_path):
                    if os.path.isdir(os.path.join(gal_path, file)):
                        print(f'Found nested gallery: {gal_path} with subdirectory: {file}')
                    elif file.lower().endswith('.jpg'):
                        self.images_in_galleries.add(file)
                        if file not in self.photos:
                            self.photos[file] = []
                        photo_ref = dict()
                        photo_ref["path"] = short_gal_path
                        photo_ref["in_gallery"] = True
                        photo_ref["gallery"] = a_dir
                        photo_ref["file"] = file
                        self.photos[file].append(photo_ref)
                        if a_dir not in self.galleries:
                            self.galleries[a_dir] = {"gallery": a_dir, "image": [file]}
                        else:
                            self.galleries[a_dir]["image"].append(file)
                    elif file.lower().startswith('metadata'):
                        pass
                    else:
                        print(f'Found non-jpg file in gallery: {gal_path}, file: {file}')
        # Create page list with a dictionary giving the pages it references
        for root, dirs, files in os.walk(self.pages_dir):
            short_path = root.split('/sst/')[1]
            for file in files:
                if file.endswith("md"):
                    if file not in self.pages:  # This allows for two pages with same name in different directories
                        self.pages[file] = []
                    page_ref = dict()
                    page_ref["path"] = root
                    page_ref["file"] = file
                    self.pages[file] = page_ref
                    self._find_pics_in_pages(page_ref)
                    page_ref["path"] = short_path  # Remove clutter directories for publishing
                    page_ref["path_key"] = self._make_path_key(page_ref)
        self.unused_images = self.image_list - self.images_in_a_page
        try:
            # Check and clean up ununsed photos and galleries
            if pvt.remove_unused_photos:
                for image in self.unused_images:
                    os.remove(WEBSITE_PATH + image)
                for dire in os.scandir(WEBSITE_PATH + "images"):
                    if os.path.isdir(dire):
                        if not os.listdir(dire):
                            os.rmdir(dire)
                for gallery in self.unused_galleries:
                    shutil.rmtree(WEBSITE_PATH + gallery)
        except Exception as e:
            foo = 3
        self.unused_galleries = self.gallery_list - self.galleries_in_a_page
        all_pages_to_sort = sorted(list(self.pages.items()), key=lambda x: x[1]['path_key'])
        context['page_list'] = all_pages_to_sort
        terminal_folders = self.find_terminal_folders()
        terminal_folders_list = sorted(list(terminal_folders.items()), key=lambda x: x[1]['folder'])
        context['terminal_folders'] = terminal_folders_list
        context['unused_images'] = self.unused_images
        context['unused_galleries'] = self.unused_galleries
        context["count_all_images"] = len(self.image_list)
        context["count_unique_image_names"] = len(self.image_names)
        context["count_gallery_images"] = len(self.images_in_galleries)
        context["count_unused_images"] = len(self.unused_images)
        context["count_unused_galleries"] = len(self.unused_galleries)
        context["count_images_used_as_singlepic"] = len(self.images_in_a_page)
        context["count_galleries"] = len(self.galleries)

        env = Environment(
            loader=FileSystemLoader(WEBSITE_PATH + 'plugins/build_photo_usage/templates'),
            autoescape=(['html']))
        template = env.get_template('build_photo_usage.tmpl')
        results = template.render(context).replace('\n', '')
        results = re.sub(" None", " ", results)  # remove occurrences of 'None'
        results = re.sub(" +", " ", results)  # remove excess whitespace
        meta_file = make_meta_file_content('Pages to Photos', 'pages_to_photos',
                                           description='Mapping of pages to photos they use')
        with open(self.outfiles_dir + '/pages_to_photos.meta', 'w') as meta_fd:
            meta_fd.writelines(meta_file)
            meta_fd.close()
        with open(self.outfiles_dir + '/pages_to_photos.html', 'w') as html_fd:
            html_fd.writelines(results)
            html_fd.close()

        template = env.get_template('build_photo_usage_summary.jinja2')
        results = template.render(context).replace('\n', '')
        results = re.sub(" None", " ", results)  # remove occurrences of 'None'
        results = re.sub(" +", " ", results)  # remove excess whitespace
        meta_file = make_meta_file_content('Photo Usage Data', 'photo_usage_data',
                                           description='Data on photo usage and unused photos and galleries')
        with open(self.outfiles_dir + '/photo_usage_data.meta', 'w') as meta_fd:
            meta_fd.writelines(meta_file)
            meta_fd.close()
        with open(self.outfiles_dir + '/photo_usage_data.html', 'w') as html_fd:
            html_fd.writelines(results)
            html_fd.close()

        template = env.get_template('build_page_usage.tmpl')
        results = template.render(context).replace('\n', '')
        results = re.sub(" None", " ", results)  # remove occurrences of 'None'
        results = re.sub(" +", " ", results)  # remove excess whitespace
        meta_file = make_meta_file_content('Pages to Photos', 'pages_to_photos',
                                           description='Mapping of pages to photos they use')
        with open(self.outfiles_dir + '/pages_directory.meta', 'w') as meta_fd:
            meta_fd.writelines(meta_file)
            meta_fd.close()
        with open(self.outfiles_dir + '/pages_directory.html', 'w') as html_fd:
            html_fd.writelines(results)
            html_fd.close()

        template = env.get_template('build_terminal_folders.tmpl')
        results = template.render(context).replace('\n', '')
        results = re.sub(" None", " ", results)  # remove occurrences of 'None'
        results = re.sub(" +", " ", results)  # remove excess whitespace
        meta_file = make_meta_file_content('Terminal Folders', 'terminal_folders',
                                           description='Sorted terminal folder list')
        with open(self.outfiles_dir + '/terminal_folders.meta', 'w') as meta_fd:
            meta_fd.writelines(meta_file)
            meta_fd.close()
        with open(self.outfiles_dir + '/terminal_folders.html', 'w') as html_fd:
            html_fd.writelines(results)
            html_fd.close()
        self.make_photo_display('/images/')
        self.make_photo_display('/galleries/')

    def make_photo_display(self, folder):
        """Build display of photos organized by folder or gallery."""
        # folder is a string of form /images/ or /galleries/
        display_list = {}
        context = {'display_list': display_list}
        for dirpath, dirnames, filenames in os.walk(WEBSITE_PATH + folder[1:]):
            if filenames:
                web_path = dirpath.split(folder)[1]
                file_list = []
                for file in filenames:
                    if not file.endswith('ml'):         # yml or yaml
                        file_list.append({'path': folder + web_path + '/' + file,
                                          'folder': web_path,
                                          'file': file })
                display_list[dirpath] = file_list
        if 'image' in folder:
            title = 'Display All Photos In Images Directory'
            slug = 'all_images_photos'
            desc = 'Display all photos in /images'
            filename = '/images_photos'
        else:
            title = 'Display All Photos in Galleries Directory'
            slug = 'all_galleries_photos'
            desc = 'Display all photos in /galleries'
            filename = '/galleries_photos'
        context['folder'] = folder[1:-1]
        context['title'] = title
        env = Environment(
            loader=FileSystemLoader(WEBSITE_PATH + 'plugins/build_photo_usage/templates'),
            autoescape=(['html']))
        template = env.get_template('build_photo_display.jinja2')
        results = template.render(context).replace('\n', '')
        results = re.sub(" None", " ", results)  # remove occurrences of 'None'
        results = re.sub(" +", " ", results)  # remove excess whitespace

        meta_file = make_meta_file_content(title, slug,  description=desc)
        with open(self.outfiles_dir + filename + '.meta', 'w') as meta_fd:
            meta_fd.writelines(meta_file)
            meta_fd.close()
        with open(self.outfiles_dir + filename + '.html', 'w') as html_fd:
            html_fd.writelines(results)
            html_fd.close()

    def find_terminal_folders(self):
        """Build list of folders that directly contain pages."""
        folder_list = dict()
        for page in self.pages:
            path = self.pages[page]["path"]  # this is the path excluding the page
            terminal = path.split('/')[-1]
            try:
                entry = folder_list[terminal]
                entry["count"] += 1
            except:
                entry = dict()
                folder_list[terminal] = entry
                entry["folder"] = terminal
                entry["count"] = 1
                entry["path"] = path
        return folder_list

    @staticmethod
    def _make_path_key(item_ref):
        # Create full path that serves as input to sort
        file = item_ref['file'].split('.')[0]       # remove file extension
        path = item_ref['path']
        return path + '/' + file

    def _find_pics_in_pages(self, page_ref):
        """Find occurrences of gallery or singlepic shortcodes in a page.
        """
        file = page_ref["file"]
        dir_path = page_ref["path"]
        page_ref["galleries"] = []
        page_ref["images"] = []
        full_path = os.path.join(dir_path, file)
        with open(full_path, 'r') as page_fd:
            page_content = '\n'.join(page_fd.readlines())
            for match in re.findall(PhotoUsage.photo_re, page_content):
                if match[0] == 'gallery':
                    # print(f'Gallery: {match[1]}')
                    tmp = match[1]
                    page_ref["galleries"].append(tmp)
                    self.galleries_in_a_page.add(tmp)
                elif match[2] == 'singlepic':
                    # print(f'Singlepic: {match[3]}')
                    tmp = match[3]
                    page_ref["images"].append(tmp)
                    self.images_in_a_page.add(tmp)   # set addition

                else:
                    print(f'MISSED: {match}, PAGE: {full_path}')


converter = PhotoUsage()


class BuildPhotoUsage(nikola.plugin_categories.Command):
    name = 'build_photo_usage'
    logger = None

    def __init__(self):
        super(BuildPhotoUsage, self).__init__()

    def _execute(self, command, args):
        self.logger = get_logger('ping', STDERR_HANDLER)
        converter.handler()
