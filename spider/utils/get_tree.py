import fnmatch
import os
from os.path import join

IGNORES = ['.git/', '*.pyc', '.DS_Store', '.idea/',
           '*.egg', '*.egg-info/', '*.egg-info', 'build/']


def ignored(ignores, path, file):
    """
    judge if the file is ignored
    :param ignores: ignored list
    :param path: file path
    :param file: file name
    :return: bool
    """
    file_name = join(path, file)
    for ignore in ignores:
        if '/' in ignore and ignore.rstrip('/') in file_name:
            return True
        if fnmatch.fnmatch(file_name, ignore):
            return True
        if file == ignore:
            return True
    return False


def get_tree(path, ignores=IGNORES):
    """
    get tree structure
    获取项目文件夹的树形结构
    :param path: Folder path
    :param ignores: Ignore files
    :return: Json
    """
    result = []
    for file in os.listdir(path):
        if os.path.isdir(join(path, file)):
            if not ignored(ignores, path, file):
                children = get_tree(join(path, file), ignores)
                if children:
                    result.append({
                        'text': file,
                        'children': children,
                        'path': path
                    })
        else:
            if not ignored(ignores, path, file):
                result.append({'text': file, 'path': path, "icon": "jstree-file"})
    return result
