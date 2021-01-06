import os
import shutil

count = 0
count_dir = 0
print("starting")
for dirpath, _, fileList in os.walk('/home/don/PycharmProjects/sst_static/sst/images/'):
    dir_last_node = dirpath.split('/')[-1]
    if dir_last_node == 'thumbs' or dir_last_node == 'cache':
        shutil.rmtree(dirpath)
        count_dir += 1
    for file in fileList:
        if 'thumbnail' in file:
            count += 1
            os.remove(dirpath + '/' + file)
print(f"Removed: {count} files and {count_dir} directories")