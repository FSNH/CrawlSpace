import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from quote.items import QuoteItem
from scrapy.loader import ItemLoader


class QuotesSpider(CrawlSpider):
    name = 'quotes'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com/']

    rules = (
        Rule(LinkExtractor(allow=r'/author/\w+', restrict_xpaths='/html/body/div[1]/div[2]/div[1]'),
             callback='parse_item'),
    )

    def parse_item(self, response):
        loader = ItemLoader(item=QuoteItem(), response=response)
        loader.add_xpath('name', '//h3[@class="author-title"]/text()')
        return loader.load_item()

