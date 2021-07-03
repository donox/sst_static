# -*- coding: utf-8 -*-
import os
import re

from nikola.plugin_categories import ShortcodePlugin
from nikola.utils import get_logger, STDERR_HANDLER
import nikola.plugin_categories
from conf import PROJECT_PATH, WEBSITE_PATH
from jinja2 import Environment, FileSystemLoader
from utilities.meta_files import make_meta_file_content


class PhotoUsage(object):
    # This shortcode creates admin pages showing photos in use and where they are used
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
                    elif file.endswith('.jpg'):
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
        self.unused_images = self.image_list - self.images_in_a_page
        self.unused_galleries = self.gallery_list - self.galleries_in_a_page
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

        template = env.get_template('build_photo_usage_summary.tmpl')
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
                    if tmp not in self.galleries_in_a_page:
                        self.galleries_in_a_page.add(tmp)
                elif match[2] == 'singlepic':
                    # print(f'Singlepic: {match[3]}')
                    tmp = match[3]
                    page_ref["images"].append(tmp)
                    if tmp not in self.images_in_a_page:
                        self.images_in_a_page.add(tmp)
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
