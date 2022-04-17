
from conf import WEBSITE_PATH
from jinja2 import Environment, PackageLoader, FileSystemLoader
import os

def process_quote(entry, position, site, env):
    """Process JSON defined story snippet and return jinja2 context entry.
    """
    try:
        context = {}
        context['quote_whole'] = "border rounded-sm border-dark  mx-auto m-2 p-2 "
        context['quote'] = entry['quote']
        try:
            context['author'] = entry['author']
        except KeyError:
            context['author'] = ''
        try:
            context['author_style'] = entry['author_style']
        except KeyError:
            context['author_style'] = ''
        try:
            context['quote_text_style'] = entry['quote_text_style']
        except KeyError:
            context['quote_text_style'] = 'color: white; font-size: larger;'
        try:
            context['quote_style'] = entry['quote_style']
        except KeyError:
            temp = 'color: white; background-color: red; text-align: center;'
            temp += 'padding-top: 15px; padding-bottom: 15px'
            context['quote_style'] = temp
        template = env.get_template('add_quote.jinja2')
        output = template.render(**context)
        return output
    except Exception as e:
        raise ValueError(f"Error in handling process_quote: {e}")
