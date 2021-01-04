import os

for dirpath, _, fileList in os.walk('/home/don/PycharmProjects/sst_static/sst/images/'):
    for file in fileList:
        if 'thumbnail' in file:
            os.remove(dirpath + '/' + file)

