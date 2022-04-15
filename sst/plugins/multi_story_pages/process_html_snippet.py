from conf import WEBSITE_PATH
from jinja2 import Environment, PackageLoader, FileSystemLoader
import os
from conf import PARENT_PATH, PROJECT_PATH, WEBSITE_PATH


def process_html_snippet(entry, position, site, env, logger):
    """HTML Snippet to be inserted as is.
    """
    try:
        path = WEBSITE_PATH + entry['story']['file_path']
        with open(path, 'r') as fd:
            output = fd.readlines()
            fd.close()
        if len(output) == 1:
            output = output[0]
        else:
            output = '\n'.join(output)
        return output
    except Exception as e:
        err_string = f"Error in handling process_html_snippet: {e}"
        logger.error(err_string)
        return None
