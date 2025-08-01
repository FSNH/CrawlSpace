import json
import logging
import time

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy_redis.spiders import RedisCrawlSpider
from quote.items import QuoteItem, CrawletemplateItem, LaaItem, InfsciItem, DingItem, ChemItem, ReagentItem, SyItem, \
    TciItem, MceItem
from scrapy.loader import ItemLoader
from scrapy.utils.project import get_project_settings


class RediscurrencySpider(CrawlSpider):
    name = 'rediscurrency'

    def __init__(self, data, *args, **kwargs):
        print(data)
        data = json.loads(data)
        # data = eval(data.replace("true", 'True'))
        self.allowed_domains: list = data.get("allowed_domains")  # 获取域名
        self.start_urls: str = data.get("start_urls")  # 获取开始网址
        # self.redis_key = f'{name}s:start_urls'
        self.rules_list: list = data.get("rules")  # 获取自定义规则
        self.item: dict = data.get("item")  # 自定义数据项item
        project_settings = get_project_settings()
        self.settings = dict(project_settings.copy())
        self.settings.update(data.get('settings'))
        # self.rules = rules.get(config.get('rules'))  # 第一种配置方式
        # 第二种配置方式
        rules = []
        for rule_kwargs in self.rules_list:
            link_extractor = LinkExtractor(**rule_kwargs.get("link_extractor"))
            rule_kwargs['link_extractor'] = link_extractor
            rule = Rule(**rule_kwargs)
            rules.append(rule)
        self.rules = rules
        print(self.rules)
        super(RediscurrencySpider, self).__init__(*args, **kwargs)

    def parse_item(self, response):
        item = self.item
        cls = eval(item.get('class'))()
        loader = eval(item.get('loader'))(cls, response=response)
        # print(eval(item.get('loader'))(cls, response=response))
        loader.add_value("source_url", response.url)  # 源链接
        loader.add_value("create_time", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))  # 采集的时间
        loader.add_value("update_time", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))  # 采集的时间
        for key, value in item.get('attrs').items():
            for extractor in value:
                if extractor.get("method") == "xpath":
                    loader.add_xpath(key, extractor.get("arg"), **{'re': extractor.get('re')})
                if extractor.get("method") == "css":
                    loader.add_css(key, extractor.get("arg"), **{'re': extractor.get('re')})
                if extractor.get("method") == "value":
                    loader.add_value(key, extractor.get("arg"), **{'re': extractor.get('re')})

        yield loader.load_item()
        if item.get("nextpage", False):
            if item.get("next_xpath", False):  # 下一页
                next_url = response.xpath(item.get("next_rule")).get()
                logging.info(next_url)
            else:
                next_url = response.css(item.get("next_rule")).get()
                logging.info(next_url)
            if next_url:
                logging.info(f"当前页:{response.url}")
                logging.info(f"下一页:{response.urljoin(next_url)}")
                yield scrapy.Request(url=response.urljoin(next_url), callback=self.parse_item)
            else:
                yield scrapy.Request(url=response.url, callback=self.parse_item)
        else:
            pass
