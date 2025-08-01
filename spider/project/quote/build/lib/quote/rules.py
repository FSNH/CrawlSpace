from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule

rules = {
    'quotes_rule': (
        Rule(LinkExtractor(allow=r'/author/\w+', restrict_xpaths='/html/body/div[1]/div[2]/div[1]'),
             callback='parse_item'),
        Rule(LinkExtractor(allow=r'/page/\d+', restrict_xpaths='//li[@class="next"]'), follow=True),
    ),
    'mce_rules': (
        Rule(LinkExtractor(allow=r'/Pathways/\w+.htm'), follow=True),
        Rule(LinkExtractor(restrict_css='ul#target_list'), follow=True,
             callback='parse_item'),)
}
