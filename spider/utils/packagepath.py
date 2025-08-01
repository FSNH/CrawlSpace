import os


class PackPath:
    def __init__(self, basepath, path):
        """
        初始化 FolderCreator 类，接受两个路径参数。
        :param basepath: 基础路径
        :param path: 需要创建的相对路径
        """
        self.basepath = basepath
        self.path = path
        self.full_path = os.path.join(basepath, path)  # 合并路径

    def create_folder(self):
        """
        创建文件夹的逻辑：
        - 如果路径存在，打印提示信息。
        - 如果路径不存在，创建文件夹并打印成功信息。
        """
        if os.path.exists(self.full_path):
            print(f"文件夹已存在：{self.full_path}")
            return True,self.full_path
        else:
            try:
                os.makedirs(self.full_path)  # 创建文件夹（包括父目录）
                print(f"文件夹创建成功：{self.full_path}")
            except Exception as e:
                print(f"文件夹创建失败：{e}")
                return False,self.full_path
            else:
                return True,self.full_path
    def get_folder_name(self):
        """
        创建文件夹的逻辑：
        - 如果路径存在，打印提示信息。
        - 如果路径不存在，创建文件夹并打印成功信息。
        """
        try:
            folder_path=self.full_path
            print(folder_path)
            files = []
            for filename in os.listdir(folder_path):
                print(filename)
                files.append(filename)
            print(files)
            return files
        except Exception as e:
            print(f"Error: {e}")
            return []

    # 示例用法


# if __name__ == "__main__":
#     # 测试路径
#     path = "sub_folder"
#
#     # 创建 FolderCreator 实例
#     basepath = os.path.abspath(join(os.getcwd(), PROJECTS_FOLDER))
#     basepath="/mnt/data/pythongit/CrawlSpace版本迭代/CrawlSpace/spider/project"
    # path="chem"
    # folder_creator = PackPath(basepath,path)
#
#     # 调用创建文件夹方法
#     folder_creator.create_folder()
#     folder_creator.get_folder_name()