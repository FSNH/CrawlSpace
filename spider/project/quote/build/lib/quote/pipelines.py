# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
import time

import redis
from itemadapter import ItemAdapter
from pymongo import MongoClient


class SpiderUrls(object):
    def __init__(self):
        self.Pool = redis.ConnectionPool(host='192.168.1.250', port=6379, max_connections=200)
        self.client = redis.Redis(connection_pool=self.Pool, decode_responses=True)
        # self.client = redis.Redis(host='121.196.202.117', port=6379, password='Chem960')
        self.k = 0

    def push_set_one(self, priority=10, cas='', url='', spidername=''):
        """
        导入cas号
        单个导入zset
        :param spidername: 爬虫名称
        :param priority: 优先级数 越大优先级越高
        :param cas:
        :param url:
        :return:
        """
        # data_dict = {10: {"url": "http://www.bomeibio.com/goods.php?id=2687"},
        #              200: {"url": "http://www.bomeibio.com/goods.php?id=2686"},
        #              30: {"url": "http://www.bomeibio.com/goods.php?id=2685"},
        #              400: {"url": "http://www.bomeibio.com/goods.php?id=2684"},
        #              500: {"url": "http://www.bomeibio.com/goods.php?id=2683"},
        #              600: {"url": "http://www.bomeibio.com/goods.php?id=2682"},
        #              }
        # data_dict = {priority: {"cas": f"{cas}"}, }
        data_dict = {priority: {"url": f"{url}", "cas": f"{cas}"}, }

        # data_dict = {100: {"url": "http://www.bomeibio.com/goods.php?id=13716"}, }
        for d, x in data_dict.items():
            print(d, x)
            score = d  # 有序集合的分数，分数越大优先级越高
            member = json.dumps(x)  # 优先级对应的参数url，类型为str
            mapping = {member: score, }  # redis zadd使用字典方式存放参数
            self.client.zadd(f'{spidername}s:start_urls', mapping)  # 正确 导入数据到redis队列
            num = self.client.zcard(f'{spidername}s:start_urls')  # 查询导入的数据量
            print(num)


class MongodbSave:
    def __init__(self):
        self.client = MongoClient(host='192.168.1.30',
                                  port=27017, maxPoolSize=None)  # 不限制连接数
        self.db = self.client["crawlspace_price_urls"]
        self.collection = self.db['price_url']

    def select_exist(self, info: dict):
        """
        数据是否存在
        :param info:
        :return:
        """
        return True if self.collection.find_one({"url": info.get("url"), "source": info.get("source")}) else False

    def update_or_insert(self, info):
        """
            update:$set数据存在就更新,$setOnInsert不存在就插入,插入及更新的数据都包含$set的数据
        """
        if info.get("url") and info.get("source"):
            if self.select_exist(info):
                self.collection.update_one({"url": info.get("url"), "source": info.get("source")},
                                           {'$set': {"update_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                                                     "async_status": 0},
                                            '$setOnInsert': info},
                                           upsert=True)
            else:
                self.collection.insert_one(info)
        else:
            pass


class QuotePipeline:
    def process_item(self, item, spider):
        data = dict(item)
        if data.get("urls"):
            for url in data.get("urls"):
                info = {"source": data.get("source"), "create_time": data.get("create_time")}
                info.update({"url": url})
                MongodbSave().update_or_insert(info)
                # SpiderUrls().push_set_one(url=url, spidername=info.get("source"))
                # spider.crawler.stats.inc_value(f"{data.get('source')}_scraped_count")
        else:
            pass

        return item


if __name__ == '__main__':
    s = MongodbSave().select_exist({"url": "https://www.medchemexpress.cn/parathyroid-hormone-1-34-rat.html", "source": "mce"})
    print(s)
    if not s:
        MongodbSave().collection.insert_one({"url": "https://www.medchemexpress.cn/parathyroid-hormone-1-34-rat.html", "source": "mce"})
