# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst, MapCompose


class QuoteItem(scrapy.Item):
    # define the fields for your item here like:
    source = scrapy.Field(output_processor=TakeFirst())  # 数据源
    urls = scrapy.Field(input_processor=MapCompose(lambda i: i))  # 详情链接
    name = scrapy.Field(output_processor=TakeFirst())  # 名称
    source_url = scrapy.Field(output_processor=TakeFirst())  # 源链接
    create_time = scrapy.Field(output_processor=TakeFirst())  # 采集时间
    update_time = scrapy.Field(output_processor=TakeFirst())  # 采集时间


class MceItem(scrapy.Item):
    # define the fields for your item here like:
    source = scrapy.Field(output_processor=TakeFirst())  # 数据源
    urls = scrapy.Field(input_processor=MapCompose(lambda i: 'https://www.medchemexpress.cn' + i))  # 详情链接
    name = scrapy.Field(output_processor=TakeFirst())  # 名称
    source_url = scrapy.Field(output_processor=TakeFirst())  # 源链接
    create_time = scrapy.Field(output_processor=TakeFirst())  # 采集时间
    update_time = scrapy.Field(output_processor=TakeFirst())  # 采集时间


class CrawletemplateItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
    name = scrapy.Field()
    categories = scrapy.Field()
    cover = scrapy.Field()
    published_at = scrapy.Field()
    score = scrapy.Field()
    drama = scrapy.Field()
    source_site = scrapy.Field(output_processor=TakeFirst())
    source_url = scrapy.Field(output_processor=TakeFirst())  # 源链接
    create_time = scrapy.Field(output_processor=TakeFirst())  # 采集时间
    update_time = scrapy.Field(output_processor=TakeFirst())  # 采集时间


class LaaItem(scrapy.Item):
    # define the fields for your item here like:
    source = scrapy.Field(output_processor=TakeFirst())  # 数据源
    urls = scrapy.Field(input_processor=MapCompose(lambda i: 'http:' + i))  # 详情链接
    name = scrapy.Field(output_processor=TakeFirst())  # 名称
    source_url = scrapy.Field(output_processor=TakeFirst())  # 源链接
    create_time = scrapy.Field(output_processor=TakeFirst())  # 采集时间
    update_time = scrapy.Field(output_processor=TakeFirst())  # 采集时间


class InfsciItem(scrapy.Item):
    # define the fields for your item here like:
    source = scrapy.Field(output_processor=TakeFirst())  # 数据源
    urls = scrapy.Field(input_processor=MapCompose(lambda i: 'http://www.infsci.com' + i))  # 详情链接
    name = scrapy.Field(output_processor=TakeFirst())  # 名称
    source_url = scrapy.Field(output_processor=TakeFirst())  # 源链接
    create_time = scrapy.Field(output_processor=TakeFirst())  # 采集时间
    update_time = scrapy.Field(output_processor=TakeFirst())  # 采集时间


class DingItem(scrapy.Item):
    # define the fields for your item here like:
    source = scrapy.Field(output_processor=TakeFirst())  # 数据源
    urls = scrapy.Field(input_processor=MapCompose(
        lambda i: 'http:' + i if i.startswith("//") else 'http://www.9dingchem.com' + i))  # 详情链接
    name = scrapy.Field(output_processor=TakeFirst())  # 名称
    source_url = scrapy.Field(output_processor=TakeFirst())  # 源链接
    create_time = scrapy.Field(output_processor=TakeFirst())  # 采集时间
    update_time = scrapy.Field(output_processor=TakeFirst())  # 采集时间


class ChemItem(scrapy.Item):
    # define the fields for your item here like:
    source = scrapy.Field(output_processor=TakeFirst())  # 数据源
    urls = scrapy.Field(input_processor=MapCompose(lambda i: 'https://www.chemenu.com' + i))  # 详情链接
    name = scrapy.Field(output_processor=TakeFirst())  # 名称
    source_url = scrapy.Field(output_processor=TakeFirst())  # 源链接
    create_time = scrapy.Field(output_processor=TakeFirst())  # 采集时间
    update_time = scrapy.Field(output_processor=TakeFirst())  # 采集时间


class ReagentItem(scrapy.Item):
    # define the fields for your item here like:
    source = scrapy.Field(output_processor=TakeFirst())  # 数据源
    urls = scrapy.Field(input_processor=MapCompose(lambda i: 'http://www.nj-reagent.com' + i.split(';')[0]))  # 详情链接
    name = scrapy.Field(output_processor=TakeFirst())  # 名称
    source_url = scrapy.Field(output_processor=TakeFirst())  # 源链接
    create_time = scrapy.Field(output_processor=TakeFirst())  # 采集时间
    update_time = scrapy.Field(output_processor=TakeFirst())  # 采集时间


class SyItem(scrapy.Item):
    # define the fields for your item here like:
    source = scrapy.Field(output_processor=TakeFirst())  # 数据源
    urls = scrapy.Field(input_processor=MapCompose(lambda i: 'http://www.shao-yuan.com' + i))  # 详情链接
    name = scrapy.Field(output_processor=TakeFirst())  # 名称
    source_url = scrapy.Field(output_processor=TakeFirst())  # 源链接
    create_time = scrapy.Field(output_processor=TakeFirst())  # 采集时间
    update_time = scrapy.Field(output_processor=TakeFirst())  # 采集时间


class TciItem(scrapy.Item):
    # define the fields for your item here like:
    source = scrapy.Field(output_processor=TakeFirst())  # 数据源
    urls = scrapy.Field(input_processor=MapCompose(lambda i: 'https://www.tcichemicals.com' + i))  # 详情链接
    name = scrapy.Field(output_processor=TakeFirst())  # 名称
    source_url = scrapy.Field(output_processor=TakeFirst())  # 源链接
    create_time = scrapy.Field(output_processor=TakeFirst())  # 采集时间
    update_time = scrapy.Field(output_processor=TakeFirst())  # 采集时间
