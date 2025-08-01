from datetime import timedelta
import datetime
from pprint import pprint
import httpx
from logparser import parse
from utils.loginfo import Logs

log = Logs()  # 配置日志文件
# 去除不需要的字段
POP_KEY = ['downloader/exception_type_count/builtins.AttributeError',
           'downloader/exception_type_count/twisted.internet.error.ConnectionRefusedError',
           'downloader/exception_type_count/twisted.internet.error.TimeoutError',
           'downloader/exception_type_count/twisted.web._newclient.ResponseNeverReceived',
           'retry/reason_count/twisted.internet.error.ConnectionRefusedError',
           'retry/reason_count/twisted.internet.error.TimeoutError',
           'retry/reason_count/twisted.web._newclient.ResponseNeverReceived',
           'downloader/exception_type_count/scrapy.core.downloader.handlers.http11.TunnelError',
           'retry/reason_count/scrapy.core.downloader.handlers.http11.TunnelError',
           'retry/reason_count/twisted.web._newclient.ResponseFailed',
           'downloader/exception_type_count/twisted.web._newclient.ResponseFailed'
           ]


class LogparserScrapyLog(object):
    def __init__(self):
        self.log_url = ""

    def init_url(self, url: str):
        """
        初始化url
        :param url:
        :return:
        """
        self.log_url = url

    def parser(self, client):
        """
        解析scrapy日志的crawler_stats
        :return:
        """
        try:
            with httpx.Client() as client_app:
                if not client.auth:
                    resplog = client_app.get(url=self.log_url, timeout=3).text
                else:
                    resplog = client_app.get(url=self.log_url, timeout=3, auth=(client.username, client.password)).text
                # print(resplog)
                results = parse(resplog)
        except Exception as e:
            log.error(e)
            return {"status": 400, "msg": str(e)}
        else:
            result_state = dict(results.get('crawler_stats'))
            if result_state:
                # 去除不需要的一些参数
                key_pop = {result_state.pop(key) for key in POP_KEY if result_state.get(key)}
                # 转化时间格式
                result_state.update({"start_time": (eval(result_state.get('start_time')) + timedelta(hours=8)).strftime(
                    "%Y-%m-%d %H:%M:%S")})
                result_state.update(
                    {"finish_time": (eval(result_state.get('finish_time')) + timedelta(hours=8)).strftime(
                        "%Y-%m-%d %H:%M:%S")})

            return result_state


if __name__ == '__main__':
    url = 'http://192.168.1.140:49211/logs/chemenu/chem/6c50dea08fb811edb35a0242ac110002.log'
    with httpx.Client() as client_app:
        log_text = client_app.get(url=url).text
        results = log_text[-500:]
        print(results)
    # result = d.parser()
    # pprint(result)


