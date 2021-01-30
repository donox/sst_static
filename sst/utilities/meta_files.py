import datetime as dt


def make_meta_file_content(title, slug, **kwargs):
    """Make a meta file as a companion for an md or html file"""
    content = f"..title: {title}\n"
    content += f"..slug: {slug}\n"
    today = dt.datetime.now()
    content += f"..date: {today.year} - {today.month} - {today.day}\n"
    for key in kwargs:
        content += f"..{key}: {kwargs[key]}\n"
    return content