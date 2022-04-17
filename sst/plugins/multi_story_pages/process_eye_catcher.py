from conf import WEBSITE_PATH
from jinja2 import Environment, PackageLoader, FileSystemLoader
import os
from conf import PARENT_PATH, PROJECT_PATH, WEBSITE_PATH


def process_eye_catcher(entry, position, site, env, logger):
    """HTML Snippet to be inserted as is.
    """
    try:
        col_number = entry['parent_context']['col_num']
        col_width = entry['parent_context']['parent_row']['cols'][col_number]['col_count']
        story = entry['story']
        path = WEBSITE_PATH + entry['story']['photo_path']
        text = entry['story']['phrase']
        context = {}
        keys = story.keys()
        if 'phrase' in keys and story['phrase']:
            context['phrase'] = story['phrase']
        if 'photo_path' in keys and story['photo_path']:
            context['photo_path'] = story['photo_path']
        if 'story_link' in keys and story['story_link']:
            context['story_link'] = story['story_link']
        if 'minimum_height' in keys:
            ht = str(story['minimum_height'])
            if not ht.endswith('px'):
                ht += 'px'
            context['height'] = ht

        else:
            context['height'] = str(col_width * 60) + 'px'
        if 'text_style' in keys:             # allow any css style attributes
            context['text_style'] = story['text_style']
        if 'image_style' in keys and story['image_style'] == 'gradient':             # allow any css style attributes
            base = "background-image: linear-gradient( rgba(0, 0, 0, 0.3), rgba(0, 0, 0, 0.3)), url('"
            base += story['photo_path'] + "');"
            context['image_style'] = base
        else:
            context['image_style'] = "background-image: url('" + story['photo_path'] + "');"
        if 'position' in keys:
            pos = str(story['position']).split(',')
            ht = int(context['height'][:-2])  # convert to a percent
            if len(pos) < 2:
                context['position_down'] = str(round(int(pos[0].strip()) * ht * 0.01)) + 'px'
            else:
                context['position_right'] = pos[0].strip()
                context['position_down'] = str(round(int(pos[1].strip()) * ht * 0.01)) + 'px'

        if 'as_background' in keys:
            context['as_background'] = story['as_background']
        else:
            context['as_background'] = False
        context['css_class'] = 'unused'
        context['title_class'] = 'unused'
        context['caption_class'] = 'caption'
        context['image_class'] = 'unused'
        context['entry_type'] = entry['entry_type']
        template = env.get_template('eye_catcher.jinja2')
        output = template.render(**context)
        return output
    except Exception as e:
        err_string = f"Error in handling process_html_snippet: {e}"
        logger.error(err_string)
        return None
