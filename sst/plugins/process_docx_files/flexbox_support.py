# -*- coding: utf-8 -*-
import re
from collections import deque


class SupportFlexbox(object):
    """Provide support for css flexbox.

    Nikola does not support nested shortcodes so we remove the "box" shortcode and
    convert it to proper html on the markdown file prior to submitting to nikola."""
    # Box start shortcode:  {{% box name="xxx" direction="row" %}}
    # Pandoc has surrounded the shortcode with <p> elements which results in broken emitted html; remove them
    box_start = r'<p>(?P<start>\{\{% +box\s+name="(?P<name_s>\w+)"'
    box_start += r'(\s+(?P<attrs>((((\w+)="((\w|:|-)+)")\s+))*))%\}\})</p>'
    box_end = r'<p>(?P<end>\{\{% +/box\s+name="(?P<name_e>\w+)"\s+%\}(?P<last_char>\}))</p>'
    # Note: DOTALL makes '.' include newlines
    box_comp_start = re.compile(box_start)
    box_comp_end = re.compile(box_end)
    box_attr = re.compile(r'(?P<attribute>\w+)="(?P<value>(\w|_|-|:|;)+)"')

    def __init__(self):
        self.stack = deque()

    def process_box_shortcodes(self, in_string, result):
        """Process next shortcode and recurse to process nested codes.

        There are three cases:
        (1) input does not match start  or end of shortcode:  return in_string
        (2) input finds first open box:
                (a) get box name, other parameters and push on stack.
                (b) recurse on tail of in_string.
        (3) input finds close box:
            (a) get name and compare to top of stack - must match or throw error.
            (b) emit html using parameters from stack and surround current in_string as returned
                from recursion.
            (c) process tail."""
        if not in_string:
            return ''

        # Determine closest box shortcode and amount of in_string before it
        start_pos_start = start_pos_end = end_pos_start = end_pos_end = None
        search_start = self.box_comp_start.search(in_string)
        if search_start:
            start_pos_start, start_pos_end = search_start.span()
        search_end = self.box_comp_end.search(in_string)
        if search_end:
            end_pos_start, end_pos_end = search_end.span()
        # Determine beginning of closest box shortcode
        if search_start and start_pos_end:
            str_beginning = min(start_pos_start, end_pos_start)
        elif search_start:
            str_beginning = start_pos_start
        elif search_end:
            str_beginning = end_pos_start
        else:
            str_beginning = len(in_string)

        if str_beginning > 0:
            result.append(in_string[0:str_beginning])
            self.process_box_shortcodes(in_string[str_beginning:], result)
        elif str_beginning == start_pos_start:
            # Process box beginning
            box_match = search_start.groupdict()
            box_match_keys = box_match.keys()
            if 'name_s' in box_match_keys:
                print(f"Matched start: {box_match['name_s']}")
                self.stack.append(box_match)
                a_tmp = box_match['attrs']
                begin_text = self._build_flex_container_start(box_match['attrs'])
                result.append(begin_text)
                # print(f"1: {in_string[match_len:]}")
                self.process_box_shortcodes(in_string[start_pos_end:], result)
                foo = 3
        elif str_beginning == end_pos_start:
            # process box end
            box_match = search_end.groupdict()
            box_match_keys = box_match.keys()
            if 'name_e' in box_match_keys:
                end_name = box_match['name_e']
                print(f"Matched end: {box_match['name_e']}")
                if not self.stack:
                    raise ValueError(f'Closing box found with no matching start')
                start_dict = self.stack[-1]
                start_name = start_dict['name_s']
                if start_name != end_name:
                    raise ValueError(f'Unmatched containers: {start_name} and {end_name}')
                self.stack.pop()
                result.append('</div>')
                self.process_box_shortcodes(in_string[end_pos_end:], result)
                foo = 3
        else:
            result.append(in_string)

    def _build_flex_container_start(self, attrs):
        attr_dict = dict()
        while True:
            parsed_attrs = self.box_attr.search(attrs)
            if not parsed_attrs:
                break
            attr_dict[parsed_attrs.group('attribute')] = parsed_attrs.group('value')
            attrs = attrs[parsed_attrs.end('value'):]
        dict_keys = list(attr_dict.keys())
        if 'direction' in dict_keys:
            dict_keys.remove('direction')
            val = attr_dict['direction']
            if val == 'row':
                cls = 'src-flex-container'
            elif val == 'row-reverse':
                cls = 'src-flex-container-rev'
            elif val == 'column' or val == 'col':
                cls = 'src-flex-container-col'
            elif val == 'column-reverse' or val == 'col-reverse':
                cls = 'src-flex-container-col-rev'
            else:
                cls = f'src-flex-container UNRECOGNIZED BOX DIRECTION {val}'
        other_attrs = []
        for key in dict_keys:
            other_attrs.append(f' {key}="{attr_dict[key]}"')
        other_attrs = ' '.join(other_attrs)
        start_str = f'<div class="{cls}" {other_attrs}>'
        return start_str


