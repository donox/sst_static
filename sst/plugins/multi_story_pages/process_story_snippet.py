
from conf import WEBSITE_PATH
from jinja2 import Environment, PackageLoader, FileSystemLoader
import os

def process_story_snippet(entry, position, site, env, err_reporter):
    """Process JSON defined story snippet and return jinja2 context entry.
    """
    try:
        story = entry['story']
        if not story:
            err_reporter.record_err(f'process_story_snippet called, but entry did not contain a story')
            return
        file_path = story['file_path']
        if not file_path:
            err_reporter.record_err(f'process_story_snippet called, but story had null file path')
        else:
            tmp = file_path.split('/')[-1]
            err_reporter.record_note(f'Story File: {tmp}')
            err_reporter.record_note(f'Story Path: {file_path}')
        with open(WEBSITE_PATH + '/' + file_path) as fd:
            story_content = ' '.join(fd.readlines())
            fd.close()
        keys = story.keys()
        if story['make_snippet']:
            # Need to create snippet that is not specified in the file itself
            # There may be an entry indicating the beginning of text NOT included in the snippet.
            if 'starting_text' in keys:
                snippet_start = story_content.find(story['starting_text'])
                if snippet_start == -1:
                    err_string = f"Snippet starting text [{story['starting_text']}] not found in story."
                    err_reporter.record_err(err_string)
                    return
            else:
                snippet_start = 0       # This does not exclude any bylines!!!!!
            if 'stopping_text' in keys:
                snippet_end = story_content.find(story['stopping_text'])
                if snippet_end == -1:
                    err_string = f"Snippet stopping text [{story['stopping_text']}] not found in story."
                    err_reporter.record_err(err_string)
                    return
            else:
                snippet_end = len(story_content)
            snippet_content = story_content[snippet_start:snippet_end]
        else:
            err_string = f"Not implemented - story['make_snippet']=False"
            err_reporter.record_err(err_string)
            return
        context = {}
        if 'title' in keys and story['title']:
            context['title'] = story['title']
        if 'byline' in keys:
            context['byline'] = story['byline'] + '\n'
            if 'photos' in keys and story['photos']:
                context['photos'] = story['photos'] + '\n'
        context['css_class'] = 'unused'
        context['title_class'] = 'unused'
        context['caption_class'] = 'unused'
        context['image_class'] = 'unused'
        context['entry_type'] = entry['entry_type']
        context['content'] = snippet_content
        # TODO: Handle file_source_path
        fp = entry['story']['file_path']
        if 'no_read_more' not in keys:
            context['read_more'] = '/' + fp[:-3] + '/'         # remove ".md"
        template = env.get_template('story_snippet.jinja2')
        output = template.render(**context)
        return output
    except Exception as e:
        err_string = f"Error in handling process_story_snippet: {e}"
        err_reporter.record_err(err_string)
