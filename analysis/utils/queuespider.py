import configparser
import json
import logging
import os
import queue
import threading
import time
from pprint import pprint

from multiprocessing import Process
from pymongo import MongoClient
from multiprocessing import Queue  # 可以用于进程之间的数据共享

logger_analysis = logging.getLogger('analysis_log')


class Readini(object):
    """
    读取配置文件
    优先读取项目配置文件，不存在再去读取根目录配置文件
    返回配置文件的路径地址
    """

    def getconfig(self):
        path_list = [os.path.abspath(os.path.join(os.getcwd(), "config.ini")),
                     os.path.join(os.path.dirname(__file__), "config.ini"),
                     ]
        config_path = ""
        config_paths = [path if os.path.exists(path) else "" for path in path_list]  # 判断配置文件是否存在
        # print(config_paths)
        for config_path in config_paths:
            if config_path:
                config_path = config_path  # 获取存在的配置文件
                break
            else:
                continue
        # print(config_path)
        return config_path  # 返回配置文件的地址


class Qspider(object):
    """
    V2.0
    数据状态：0 or ""：待处理;1：正在处理;2:处理完成
    Getconnect：链接数据库
    ExecDataSelectSql:生产者
    Consume:消费者（queue队列）
    Scheduler:调度器
    nextdata:获取下一个数据
    _update_sync：更新数据获取状态为1
    update_sync_complate：更新数据获取状态为2
    savelist：批量保存数据
    ExecInsertSql：单个保存数据
    get_now：获取当前时间
    make_data_from_queue：获取队列数据并执行相关处理逻辑
    start：运行程序
    """

    def __init__(self):
        self.config = configparser.ConfigParser()
        # -read读取ini文件
        self.config_path = Readini().getconfig()
        self.config.read(self.config_path, encoding='utf-8-sig')  # 优先读取根目录，不存在再去读取项目配置文件
        self.client = None
        self.db = None
        self.collection = None
        self.Getconnect()  # 初始化数据库链接
        self.queue = Queue(10)  # 队列，先进先出，队列长度为50个
        self.update_state = "url_pickstatus"  # 默认的更新字段
        self.filter_sql = '{"$and": [{"url_pickstatus": {"$ne": 2}}, {"url_pickstatus": {"$ne": 1}}]}'  # 获取数据的默认条件

    def Getconnect(self):
        """
        创建数据的查询的游标
        可以重写该方法添加多个游标
        """
        try:
            # print(settings.MONGO.host, settings.MONGO.port, settings.MONGO.database, settings.MONGO.productinfo)
            self.client = MongoClient(host=self.config.get('analysis', 'host'),
                                      port=int(self.config.get('analysis', 'port')), maxPoolSize=None)  # 不限制连接数
        except Exception as e:
            logger_analysis.error(f"数据库连接报错：{e}")
            # self.log.info(f"数据库连接报错：{e}")
        else:
            self.db = self.client.get_database(self.config.get('analysis', 'db'))  # 数据库不存在就创建
            self.collection = self.db.get_collection(self.config.get('analysis', 'collection'))  # 集合不存在就创建

    def savelist(self, collect, infos: list):
        """
        批量保存到mongodb
        """
        results = []
        try:
            for info in infos:
                time_dict = {"url_pickdate": self.get_now}  # 采集时间(默认添加的字段)
                info.update(time_dict)
                results.append(info)
        except Exception as e:
           logger_analysis.error(f"信息存入数据报错!{e}")
        else:
            collect.insert_many(results)
            logger_analysis.info("信息存入成功！")

    def ExecInsertSql(self, collect, info: dict):
        try:
            info.update({"url_pickdate": self.get_now})
            collect.insert_one(info)
        except Exception as e:
            logger_analysis.error(f"信息存入数据报错!{e}")
        else:
            logger_analysis.info("信息存入成功！")

    def ExecInsertManySql(self, collect, info: list):
        try:
            collect.insert_many(info)
        except Exception as e:
            logger_analysis.error(f"信息存入数据报错!{e}")
        else:
            logger_analysis.info("信息批量存入成功！")

    def ExecDataSelectSql(self):
        info = json.loads(self.filter_sql)  # 执行查询的条件（可以重写）
        """
        执行获取mongodb数据并存储到queue队列中
        info: 查询条件可以自定义，默认为:{"url_pickstatus": {"$nin": [1, 2]}}
        """
        print("正在获取数据中。。。。。。")
        results = self.collection.find(info, no_cursor_timeout=True).limit(10)
        # print(results)
        for result in results:
            # print(result)
            self._update_sync(self.collection, **{"_id": result.get("_id")})
            logger_analysis.info(f"成功获取到数据{result.get('_id')}")
            # 当队列为空的时候 ，get_nowait 一样会触发 queue.Empty 异常
            try:
                self.queue.put_nowait(result)
            except queue.Full:
                logger_analysis.info("队列已满!")

    @property
    def get_now(self):
        """获取当前的时间"""
        return time.strftime('%Y-%m-%d %H-%M-%S', time.localtime())

    def consumequeue(self):
        """
        消费queue队列数据
        """
        # block参数的功能是,如果这个队列为空则阻塞，
        # timeout和上面一样，如果阻塞超过了这个时间就报错，如果想一只等待这就传递None
        try:
            data = self.queue.get(block=True, timeout=None)
        except queue.Empty:
            logger_analysis.warning("队列为空......")
        else:
            logger_analysis.info(f"正在加载数据-{data.get('_id')}")
            yield data

    def Scheduler(self):
        """"
        从对列中循环调度数据，直到队列中的数据为空，并返回迭代器
        可以重写Scheduler方法，更换获取队列的数据源，例如更换成redis
        """
        while not self.queue.empty():
            for data in self.consumequeue():
                yield data
        else:
            self.ExecDataSelectSql()

    def nextdata(self):
        """
        循环获取下一条数据，调用：make_data_from_queue(data)函数生成下一条数据
        """
        while True:
            for data in self.Scheduler():
                self.make_data_from_queue(data)
            if self.queue.empty():  # 如果队列为空则停止运行
                break

    def make_data_from_queue(self, data):
        """
        该方法了必须（可以）重写，获取data数据
        返回可迭代的对象
        """
        # print(data)
        yield data

    def _update_sync(self, collection, **f_info):
        """
        collection: 集合名称
        f_info: 更新状态的条件
        更新状态为正在处理：1
        返回处理的数据量
        """
        # print(self.update_state)
        nums = collection.update_many(f_info, {'$set': {self.update_state: 1}})
        logger_analysis.info({"result": 1, "nums": nums.modified_count})
        # pprint({"result": 1, "nums": nums.modified_count})

    def update_sync_complate(self, collection, **f_info):
        """
        collection: 集合名称
        f_info: 更新状态的条件
        更新状态为处理完成：2
        返回处理完成的数据量
        """

        nums = collection.update_many(f_info, {'$set': {self.update_state: 2}})
        pprint({"result": 2, "nums": nums.modified_count})
        logger_analysis.info("数据处理成功！")

    def start(self):
        self.nextdata()

    def run_threads(self, nums: int = 25):
        """
        多线程执行
        """
        threads = []
        for _ in range(nums):  # 循环创建500个线程
            t = threading.Thread(target=self.nextdata())
            threads.append(t)
        for t in threads:  # 循环启动500个线程
            t.start()


# if __name__ == '__main__':
#     start = time.time()
#     print(start)
#     client = Qspider()
#     client.start()
    # client.run_threads()
    # end = time.time()
    # print(end)
    # cost = end - start
    # print(f"总共耗时多少{cost}")
