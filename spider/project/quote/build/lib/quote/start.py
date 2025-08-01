import json

from scrapy.cmdline import execute
from utils.Read_configs import get_config

custom_settings = get_config(name='mce')
data = json.dumps(custom_settings)

print(data)
execute(["scrapy", "crawl", "rediscurrency", "-a", f"data={data}"])
