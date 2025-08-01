# -*- coding: utf-8 -*- 
# @Time : 2024/8/15 下午4:45
# @Author : zhaomeng
# @File : get_egg_list.py
# @desc:  # 获取部署项目的历史打包记录,以egg结尾
import os
from CrawlSpace.settings import PROJECTS_FOLDER


# folder_paths = os.path.join("/".join(os.getcwd().split("/")[:-2]), PROJECTS_FOLDER)  # 本地文件中测试路经
# print(folder_paths)


def get_file_paths(folder: str) -> dict:
    # folder项目名称
    try:
        folder_path = os.path.join(folder_paths, folder)
        # print(folder_path)
        file_paths = []
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                if file_path.endswith("egg"):
                    file_paths.append(file_path)
        # print(file_paths)
    except FileNotFoundError:
        return {}
    else:
        return {"egg_list": file_paths}


def del_file_paths(project_name: str, cpath:str,egg_name: str) -> dict:
    # 删除项目的打包文件
    try:
        folder_path = os.path.join(PROJECTS_FOLDER, cpath,project_name, egg_name)
        # print(folder_path)
        flag = os.path.exists(folder_path)  # 判断文件是否存在
        print(flag)
        if flag:
            os.remove(folder_path)  # 存在就移除
        else:
            return {"status": 400, "message": "数据包已经删除"}
    except Exception as e:
        return {"status": 400, "message": str(e)}
    else:
        return {"status": 200, "message": "删除成功"}

# d = del_file_paths("abcr", "abcr_2022-06-09T10_34_51.egg")
# #
# print(d)
