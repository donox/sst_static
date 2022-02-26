import datetime as dt
import re


def make_meta_file_content(title, slug, **kwargs):
    """Make a meta file as a companion for an md or html file"""
    content = f"..title: {title}\n"
    content += f"..slug: {slug}\n"
    today = dt.datetime.now()
    content += f"..date: {today.year} - {today.month} - {today.day}\n"
    for key in kwargs:
        content += f"..{key}: {kwargs[key]}\n"
    return content


def read_meta_file(filepath):
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
