import os
import shutil

# This is used to import images from Wordpress and delete WP thumbnail our cache files which are
# not needed by Nikola.  This module can be discarded when WP Imports are not longer needed.
count = 0
count_dir = 0
print("starting")
for dirpath, _, fileList in os.walk('images/'):
    dir_last_node = dirpath.split('/')[-1]
    if dir_last_node == 'thumbs' or dir_last_node == 'cache' or dir_last_node == 'dynamic':
        shutil.rmtree(dirpath)
        count_dir += 1
    for file in fileList:
        if 'thumbnail' in file:
            count += 1
            os.remove(dirpath + '/' + file)
print(f"Removed: {count} files and {count_dir} directconf.pyories")