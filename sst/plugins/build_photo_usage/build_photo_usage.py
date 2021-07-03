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

    def handler(self, *args, **kwargs):
        # Build context for creating display pages with jinja templates
        context = {'all_pages': self.pages, 'all_photos': self.photos, 'all_galleries': self.galleries}
        for root, dirs, files in os.walk(self.images_dir):
            short_path = root.split('/sst/')[1]
            for file in files:
                if file not in self.photos:
                    self.photos[file] = []
                photo_ref = dict()
                photo_ref["path"] = short_path
                photo_ref["file"] = file
                photo_ref["in_gallery"] = False
                self.photos[file].append(photo_ref)
        for root, dirs, files in os.walk(self.galleries_dir):
            for a_dir in dirs:
                gal_path = os.path.join(root, a_dir)
                short_gal_path = gal_path.split('/sst/')[1]
                for file in os.listdir(gal_path):
                    if os.path.isdir(os.path.join(gal_path, file)):
                        print(f'Found nested gallery: {gal_path} with subdirectory: {file}')
                    elif file.endswith('.jpg'):
                        print(f'Found Gallery file: {file} in gallery: {a_dir} that is not in directory images.')
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

        env = Environment(
            loader=FileSystemLoader(WEBSITE_PATH + 'plugins/build_photo_usage/templates'),
            autoescape=(['html']))
        template = env.get_template('build_photo_usage.tmpl')
        results = template.render(context).replace('\n', '')
        results = re.sub(" None", " ", results)  # remove occurrences of 'None'
        results = re.sub(" +", " ", results)  # remove excess whitespace
        meta_file = make_meta_file_content('Pages to Photos', 'pages-to-photos',
                                           description='Mapping of pages to photos they use')
        with open(self.outfiles_dir + '/pages_to-photos.meta', 'w') as meta_fd:
            meta_fd.writelines(meta_file)
            meta_fd.close()
        with open(self.outfiles_dir + '/pages_to-photos.html', 'w') as html_fd:
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
                    page_ref["galleries"].append(match[1])
                elif match[2] == 'singlepic':
                    # print(f'Singlepic: {match[3]}')
                    page_ref["images"].append(match[3])
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
