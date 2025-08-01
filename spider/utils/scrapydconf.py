"""
scrapyd的全局配置参数
"""
import httpx
import requests
from scrapyd_api import ScrapydAPI


class ScrapydConf(object):
    """通用爬虫默认的scrapyd服务器"""

    def __init__(self):
        self.scrapyd_ip_port = "http://127.0.0.1:6800"
        self.project_name = 'quote'
        self.spider_name = 'rediscurrency'

    @property
    def scrapyd_url(self):
        """
        返回scrapyd的配置部署链接
        :return:
        """
        return self.scrapyd_ip_port

    @property
    def project(self):
        """
        返回全局的项目名称
        :return:
        """
        return self.project_name

    @property
    def spidername(self):
        """
        返回全局的爬虫名称
        :return:
        """
        return self.spider_name

    def scrapyd_init(self):
        """初始化scrapyd服务"""
        scrapydapi = ScrapydAPI(target=self.scrapyd_ip_port)
        return scrapydapi


def get_scrapyd(client):
    if not client.auth:
        return ScrapydAPI(target=scrapyd_url(client.ip, client.port), timeout=3)
    return ScrapydAPI(target=scrapyd_url(client.ip, client.port), auth=(client.username, client.password), timeout=1)


def scrapyd_url(ip, port):
    """
    get scrapyd url
    :param ip: host
    :param port: port
    :return: string
    """
    url = 'http://{ip}:{port}'.format(ip=ip, port=port)
    return url


def node_url(client):
    """
    获取节点的运行状态
    :param client: client对象
    :return:
    """
    host_ip = scrapyd_url(client.ip, client.port)
    node_url = host_ip + "/daemonstatus.json"
    return node_url


def get_node_info(client):
    url = node_url(client)
    try:
        with httpx.Client() as client_http:
            if not client.auth:
                node_info = client_http.get(url=url, timeout=3).json()
                # print(node_info)
            else:
                node_info = client_http.get(url=url, auth=(client.username, client.password), timeout=3).json()
                # print(node_info)
    except Exception as e:
        return {'status': 400, 'error': str(e)}
    else:
        return node_info
