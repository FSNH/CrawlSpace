import os

from CrawlSpace.settings import PROJECTS_FOLDER, EDIT_FOLDER


def get_code(name):
    """
    获取配置规则的文件
    :param name:
    :return:
    """
    if name and 'json' in name:
        flag = os.path.exists(os.path.join(EDIT_FOLDER, name))
        if flag:
            with open(os.path.join(EDIT_FOLDER, name), "r+") as f:
                code = f.readlines()
            if code:
                return {"code": "".join(code).strip(), "status": 200}
            else:
                return {"msg": "数据为空", "status": 400}
        else:
            return {"msg": '文件不存在', "status": 400}
    pass
