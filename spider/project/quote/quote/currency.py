import logging
import time
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from quote.utils.Read_configs import get_config
from scrapy_redis.spiders import RedisCrawlSpider
from quote.rules import rules
from quote.items import QuoteItem, CrawletemplateItem, LaaItem, InfsciItem, DingItem, ChemItem, ReagentItem, SyItem, \
    TciItem, MceItem
from scrapy.loader import ItemLoader


class CurrencySpider(RedisCrawlSpider):
    name = 'currency'

    # custom_settings = {
    #     # 自定义settings参数
    #     'SCHEDULER': "scrapy_redis.scheduler.Scheduler",  # 启用Redis调度存储请求队列
    #     'DUPEFILTER_CLASS': "scrapy_redis.dupefilter.RFPDupeFilter",  # 确保所有的爬虫通过Redis去重
    #     'SCHEDULER_PERSIST': True,  # 不清除Redis队列这样可以暂停/恢复 爬取
    #     'REDIS_START_URLS_AS_ZSET': True,  # 使用有序集合
    #     'REDIS_START_URLS_KEY': f'{name}s:start_urls',
    #     'STATS_CLASS': "scrapy_redis.stats.RedisStatsCollector",  # 将日志信息保存到redis
    #     # 'REDIS_HOST': "web.test.web960.com",
    #     # 'REDIS_PORT': "32002",
    # }

    def __init__(self, name, *args, **kwargs):
        config = get_config(name)
        self.config = config
        self.allowed_domains = config.get('allowed_domains')
        self.start_urls = config.get('start_urls')
        self.redis_key = f'{name}s:start_urls'
        # self.rules = rules.get(config.get('rules'))  # 第一种配置方式
        # 第二种配置方式
        rules = []
        for rule_kwargs in config.get("rules"):
            link_extractor = LinkExtractor(**rule_kwargs.get("link_extractor"))
            rule_kwargs['link_extractor'] = link_extractor
            rule = Rule(**rule_kwargs)
            rules.append(rule)
        self.rules = rules
        super(CurrencySpider, self).__init__(*args, **kwargs)

    def parse_item(self, response):
        item = self.config.get('item')
        cls = eval(item.get('class'))()
        loader = eval(item.get('loader'))(cls, response=response)
        # print(eval(item.get('loader'))(cls, response=response))
        loader.add_value("source_url", response.url)  # 源链接
        loader.add_value("pickup_time", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))  # 采集的时间
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
