import json
import time

from analysis.utils.queuespider import Qspider


class Analysis(Qspider):
    def __init__(self):
        super(Analysis, self).__init__()

    def get_links(self):
        """
              统计数据源所有的分析数据
              """
        # 总数据量
        price_count = self.collection.find({}).count()
        print(price_count)
        # 当前的总的本月新增数据量
        query_price_increase_count = {"create_time": {"$gt": time.strftime('%Y-%m-1')}}
        price_increase_count = self.collection.find(query_price_increase_count).count()
        print(f"当前的总的本月新增数据量{time.strftime('%Y-%m-1')}:{price_increase_count}")
        # 本月更新的总的数据量
        query_price_update_count = {"update_time": {"$gt": time.strftime('%Y-%m-1')}}
        price_update_count = self.collection.find(query_price_update_count).count()
        print(f"本月更新的总的数据量{time.strftime('%Y-%m-1')}:{price_update_count}")
        # 本月单个数据源新增的总的数据量
        query_price_per_increase_count = {'source': 'mce', 'update_time': {'$gt': time.strftime('%Y-%m-1')}}
        query_price_per_increase_count = self.collection.find(query_price_per_increase_count).count()
        print(f"本月单个数据源新增的总的数据量{time.strftime('%Y-%m-1')}:{query_price_per_increase_count}")
        # 本月单个数据源更新的总的数据量
        query_price_per_update_count = {'source': 'mce', 'update_time': {'$gt': time.strftime('%Y-%m-1')}}
        query_price_per_update_count = self.collection.find(query_price_per_update_count).count()
        print(f"本月单个数据源更新的总的数据量{time.strftime('%Y-%m-1')}:{query_price_per_update_count}")
        # 聚合查询每个数据源总的数据量
        query_price_per_count = self.collection.aggregate([
            {"$group": {
                "_id": "$source",
                "SourceCount": {"$sum": 1}
            }}
        ])
        query_price_per_count = [s for s in query_price_per_count]
        print(f"每个数据源的总数:{query_price_per_count}")
        # 聚合查询每个数据源总的更新数据量
        query_price_per_update_count = self.collection.aggregate([
            {"$match": {'update_time': {'$gt': time.strftime('%Y-%m-1')}}},
            {"$group": {
                "_id": "$source",
                "SourceCount": {"$sum": 1}
            }}
        ])
        query_price_per_update_count = [s for s in query_price_per_update_count]
        print(f"每个数据源更新的总数:{query_price_per_update_count}")

    def get_all_count(self):
        """
        数据源数据统计分析:
        总的数据量
        本月总的更新量
        本月总的新增量
        :return:
        """
        # 总数据量
        price_count = self.collection.find({}).count()

        # print(price_count)
        # 当前的总的本月新增数据量
        query_price_increase_count = {"create_time": {"$gte": time.strftime('%Y-%m-01')},
                                      "update_time": {"$exists": False}}
        price_increase_count = self.collection.find(query_price_increase_count).count()
        # print(f"当前的总的本月新增数据量{time.strftime('%Y-%m-1')}:{price_increase_count}")
        # 本月更新的总的数据量
        query_price_update_count = {"update_time": {"$gte": time.strftime('%Y-%m-01')}}
        price_update_count = self.collection.find(query_price_update_count).count()
        # print(f"本月更新的总的数据量{time.strftime('%Y-%m-1')}:{price_update_count}")
        return json.dumps({'query_price_update_count': price_update_count,
                           'query_price_increase_count': price_increase_count,
                           'price_count': price_count})

    def get_groupby_source_count(self):
        # 聚合查询每个数据源总的数据量
        query_price_per_count = self.collection.aggregate([
            {"$group": {
                "_id": "$source",
                "SourceCount": {"$sum": 1}
            }}
        ])
        query_price_per_count = [s for s in query_price_per_count]
        # print(f"每个数据源的总数:{query_price_per_count}")
        return json.dumps({"per_source_count": query_price_per_count})

    def get_groupby_source_update_count(self):
        # 聚合查询每个数据源总的更新数据量
        query_price_per_update_count = self.collection.aggregate([
            {"$match": {'update_time': {'$gte': time.strftime('%Y-%m-01')}}},
            {"$sort": {"_id": -1}},
            {"$group": {
                "_id": "$source",
                "SourceCount": {"$sum": 1}
            }}
        ])
        query_price_per_update_count = [s for s in query_price_per_update_count]
        print(f"每个数据源更新的总数:{query_price_per_update_count}")
        return json.dumps({"per_source_count": query_price_per_update_count})
        # return query_price_per_update_count

    def get_groupby_source_increase_count(self):
        # 聚合查询每个数据源总的新增数据量
        query_price_per_ncrease_count = self.collection.aggregate([
            {"$match": {'create_time': {'$gte': time.strftime('%Y-%m-01')}, "update_time": {'$exists': False}}},
            {"$sort": {"_id": -1}},
            {"$group": {
                "_id": "$source",
                "SourceCount": {"$sum": 1}
            }}
        ])
        query_price_per_increase_count = [s for s in query_price_per_ncrease_count]
        print(f"每个数据源新增的总数:{query_price_per_increase_count}")
        return json.dumps({"per_source_count": query_price_per_increase_count})
        pass


# if __name__ == '__main__':
#     obj = Analysis()
#     obj.get_groupby_source_increase_count()
#     obj.get_groupby_source_update_count()
#     obj.get_groupby_source_count()
#     obj.get_all_count()
