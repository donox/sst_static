import re
import os
import shutil
import pandas as pd

# TO CREATE DATA for self.pics DataFrame:
#   (1) Download WP database and fix default dates
#       sed -i 's/0000-00-00/2000-01-01/' /home/don/Downloads/db.sql
#   (2) Extract csv (/files/pics.csv)
#       select t1.pid, t1.filename, t1.alttext, t1.imagedate, t1.description, t2.path from wp_ngg_pictures as t1
#           join wp_ngg_gallery as t2 on t1.galleryid = t2.gid order by  t1.pid;


class HandlePictureImports(object):
    def __init__(self):
        self.run_jinja_template = None
        self.web_source = '../sst/images'
        self.pics = pd.read_csv(''.join([os.getcwd(), '/files/pics.csv']),
                                names=['pid', 'filename', 'alttext', 'imagedate', 'caption', 'path'])
        self.pics.path = self.pics.path.apply(lambda x: x.replace('/wp-content/gallery/', ''))
        self.pics.path = self.pics.path.apply(lambda x: x.replace('wp-content/gallery/', ''))
        self.pics.set_index('pid', inplace=True)

    def set_jinja(self, jinja_proc):
        # Avoid circular import, let shortcode manager pass function
        self.run_jinja_template = jinja_proc

    def remove_unnecessary_wp_folders(self):
        for dirpath, _, _ in os.walk(self.web_source):
            last_segment = os.path.split(dirpath)[1]
            if last_segment in ['cache', 'dynamic', 'thumbs']:
                shutil.rmtree(dirpath)

    def get_path_for_pic_id(self, pic_id):
        if pic_id in self.pics.index:
            return '/images/' + self.pics.path.loc[pic_id] + self.pics.filename.loc[pic_id]
        else:
            return None         # TODO: Create valid file path indicating non-existent pic