import errno
import glob
import logging
import os
import shutil
import sys
import tempfile
import traceback
from os.path import join
from subprocess import check_call

from CrawlSpace.settings import PROJECTS_FOLDER
from spider.utils.config import config


def build_project(project, version):
    """
    build project
    :param version: 版本号
    :param project:
    :return:
    """

    egg = build_egg(project, version)
    logging.info('successfully build project %s to egg file %s version %s', project, egg, version)
    return egg


_SETUP_PY_TEMPLATE = \
    '''# Automatically created by: sparrow
from setuptools import setup, find_packages
setup(
    name='%(project)s',
    version='%(version)s',
    packages=find_packages(),
    entry_points={'scrapy':['settings=%(settings)s']},
)'''


def retry_on_eintr(function, *args, **kw):
    """Run a function and retry it while getting EINTR errors"""
    while True:
        try:
            return function(*args, **kw)
        except IOError as e:
            if e.errno != errno.EINTR:
                raise


# build Egg
def build_egg(project, version):
    '''
    打包egg文件
    build project to egg file
    :param version: 版本号
    :param project:
    :return:
    '''
    work_path = os.getcwd()
    try:
        path = os.path.abspath(join(os.getcwd(), PROJECTS_FOLDER))
        project_path = join(path, project)
        os.chdir(project_path)
        settings = config(project_path, 'settings', 'default')
        setup_file_path = join(project_path, 'setup.py')
        create_default_setup_py(
            setup_file_path, settings=settings, project=project, version=version)
        d = tempfile.mkdtemp(prefix='sparrow-')
        o = open(os.path.join(d, 'stdout'), 'wb')
        e = open(os.path.join(d, 'stderr'), 'wb')
        retry_on_eintr(check_call, [sys.executable, 'setup.py', 'clean', '-a', 'bdist_egg', '-d', d],
                       stdout=o, stderr=e)
        o.close()
        e.close()

        egg = glob.glob(os.path.join(d, '*.egg'))[0]
        # Delete Origin file
        # if find_egg(project_path):
        #     os.remove(join(project_path, find_egg(project_path)))
        shutil.move(egg, join(project_path))
        return join(project_path, find_egg(project_path)[0])
    except Exception as e:
        traceback.print_exc()
        logging.error('error occurred %s', e.args)
    finally:
        os.chdir(work_path)


def find_egg(path):
    """
    find egg from path
    :param path:
    :return:
    """
    items = os.listdir(path)
    eggs_list = []
    for name in items:
        if name.endswith('.egg'):
            # return name
            eggs_list.append(name)
    return eggs_list


def create_default_setup_py(path, **kwargs):
    """
    create setup.py file to path
    :param path:
    :param kwargs:
    :return:
    """

    # if os.path.exists(path):
    #     logging.debug('setup.py file already exists at %s', path)
    # else:

    with open(path, 'w', encoding='utf-8') as f:
        file = _SETUP_PY_TEMPLATE % kwargs
        f.write(file)
        f.close()
        logging.debug('successfully created setup.py file at %s', path)

