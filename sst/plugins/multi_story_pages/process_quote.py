
from conf import WEBSITE_PATH
from jinja2 import Environment, PackageLoader, FileSystemLoader
import os

def process_quote(entry, position, site, env):
    """Process JSON defined story snippet and return jinja2 context entry.
    """
    try:
        context = {}
        context['quote'] = entry['Quote']
        try:
            context['author'] = entry['Author']
        except:
            context['author'] = ''
        template = env.get_template('add_quote.jinja2')
        output = template.render(**context)
        return output
    except Exception as e:
        raise ValueError(f"Error in handling process_quote: {e}")
