# -*- coding: utf-8 -*-

from nikola.plugin_categories import ShortcodePlugin
# this is a reference to another package at the same level
import importlib
from nikola.utils import get_logger, STDERR_HANDLER
import re
from PIL import Image
from conf import WEBSITE_PATH

# NEED TO INSTALL PYTHON SUPPORT FOR IPTC and pull caption, etc from pics
# Also need to do it for gallery - Can we push WP data into pics in prepass?

class Singlepic(ShortcodePlugin):
    name = 'singlepic'

    def __init__(self):
        self.site = None

    def set_site(self, site):
        self.site = site
        # self.inject_dependency('render_posts', 'render_galleries')
        # site.register_shortcode("gallery", self.handler)
        return super().set_site(site)

    def handler(self, *args, **kwargs):
        kw = {
            'output_folder': self.site.config['OUTPUT_FOLDER'],
        }
        context = {}
        keys = kwargs.keys()
        post = kwargs['post']

        context['image_path'] = ''
        image_width = image_height = None
        if 'image' in keys:
            image_path = kwargs['image']
            if image_path:                      # Defending against missing image_path
                context['image_path'] = image_path
                tmp = WEBSITE_PATH + image_path[1:]
                im = Image.open(tmp)
                image_width, image_height = im.size

        context['has_borders'] = True
        if 'has_borders' in keys and (kwargs['has_borders'] == 'False' or kwargs['has_borders'] == 'No'):
            context['has_borders'] = False

        possible_width = image_width
        if 'width' in keys:
            possible_width = kwargs['width']
        if 'w' in keys:
            possible_width = kwargs['w']
        if type(possible_width) is str:
            if possible_width.endswith('px'):
                possible_width = possible_width[:-2]
            if possible_width.isnumeric():
                possible_width = int(possible_width)        # defend against improper width spec
        if not possible_width:
            possible_width = 300

        possible_height = image_height
        if 'height' in keys:
            possible_height = kwargs['height']
        if 'h' in keys:
            possible_height = kwargs['h']
        if type(possible_height) is str:
            if possible_height.endswith('px'):
                possible_height = possible_height[:-2]
            if possible_height.isnumeric():
                possible_height = int(possible_height)
        if not possible_height:
            possible_height = 300
        if image_width and image_height:            # Defending against missing image_path
            image_aspect_ratio = image_height/image_width
            possible_aspect_ratio = possible_height/possible_width
            if image_aspect_ratio > possible_aspect_ratio:
                possible_width = possible_height / image_aspect_ratio
            elif image_aspect_ratio < possible_aspect_ratio:
                possible_height = possible_width * image_aspect_ratio
            else:
                pass
        context['width'] = int(possible_width)
        context['height'] = int(possible_height)

        try:
            context['border_width'] = str(context['width'] + 20) + 'px'  # size of left/right borders
        except:
            context['border_width'] = str(context['width']) + 'px'

        try:
            context['border_height'] = str(context['height'] + 20) + 'px'  # size of top/bottom borders
        except:
            context['border_height'] = str(context['height']) + 'px'

        context['alignment'] = 'float-none'
        if 'align' in keys:
            direct = kwargs['align']
        elif 'alignment' in keys:
            direct = kwargs['alignment']
        else:
            direct = None
        if direct == 'right':
            context['alignment'] = 'float-right'
        elif direct == 'left':
            context['alignment'] = 'float-left'
        elif direct == 'center':
            context['alignment'] = 'center_image'
        else:
            context['alignment'] = 'float-none'

        context['caption'] = ''         # TODO: Need to pick up title and caption
        if 'caption' in keys:
            context['caption'] = kwargs['caption']

        context['title'] = ''
        if 'title' in keys:
            context['title'] = kwargs['title']

        context['photographer'] = 'Photographer'
        context['description'] = ''
        context['css_class'] = ''
        context['title_class'] = ''
        context['caption_class'] = ''
        context['image_class'] = ''
        folder = post.folder
        post_name = post.post_name
        source_path = post.source_path
        site = kwargs['site']
        deps = []  # WHAT IS THIS FOR

        context['lang'] = ''
        context['crumbs'] = []
        context['folders'] = []
        context['permalink'] = '#'
        context.update(self.site.GLOBAL_CONTEXT)
        context.update(kw)
        output = self.site.template_system.render_template(
            'singlepic.tmpl',
            None,
            context
        )
        return output, deps

    def read_meta_file(self, filepath):
        res_dict = {}
        re_line = re.compile('\.\. (\w+): (.*)\n')
        # ..wp - status: publish
        with open(filepath, 'r') as fd:
            for line in fd:
                matched_res = re.match(re_line, line)
                try:
                    v1 = matched_res.group(1)
                    v2 = matched_res.group(2)
                    res_dict[v1] = v2
                except Exception as e:
                    print(f'BROKEN LINE?: {line}')
        return res_dict
