import sys
from scrapy.utils.project import get_project_settings
from utils.Read_configs import get_config
from scrapy.crawler import CrawlerProcess


def run(name):
    """
    运行每一个爬虫
    :param name: 配置文件
    :return:
    """
    # name = sys.argv[1]
    # name = 'test'
    custom_settings = get_config(name=name)
    spider = custom_settings.get('spider', 'currency')
    project_settings = get_project_settings()
    settings = dict(project_settings.copy())
    settings.update(custom_settings.get('settings'))
    process = CrawlerProcess(settings)
    process.crawl(spider, **{'name': name})
    process.start()


if __name__ == '__main__':
    # run(name='infsi')
    run(name='abcr')
    # run(name='nj-reagent')
