import platform
OXLEY_PATH = '~/PycharmProjects/'
IONOS_PATH = '~/homepages/11/d835068234/htdocs/'
PATTERSON_PATH = '~/'

node = platform.node()
THIS_PATH = IONOS_PATH
if node == 'Descartes':
    THIS_PATH = OXLEY_PATH
