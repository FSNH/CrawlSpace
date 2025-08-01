import logging
import logging.handlers
import time
from pathlib import Path
from CrawlSpace.settings import PROJECTS_FOLDER


class Logs(object):
    """
    日志类，日志分流
    """

    def __init__(self):
        log_dir = Path(f'{PROJECTS_FOLDER}/logs')
        if not log_dir.is_dir():
            log_dir.mkdir(parents=True)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        logfilename = f'{time.time()}.log'
        logfilepath = str(log_dir / logfilename)

        console = logging.StreamHandler()
        console.setLevel(logging.INFO)

        rotatfile = logging.handlers.RotatingFileHandler(logfilepath, 'a', 20971520, 2, 'utf-8')
        rotatfile.setLevel(logging.DEBUG)

        if not self.logger.handlers:
            self.logger.addHandler(console)
            self.logger.addHandler(rotatfile)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        console.setFormatter(formatter)
        rotatfile.setFormatter(formatter)

    def warning(self, log_message):
        self.logger.warning(log_message)

    def info(self, log_message):
        self.logger.info(log_message)

    def critical(self, log_message):
        self.logger.critical(log_message)

    def error(self, log_message):
        self.logger.error(log_message)

    def debug(self, log_message):
        self.logger.debug(log_message)


"""
使用如下：
LOG = Logs()
 
LOG.debug('This is a loggging debug message')
LOG.info('This is a loggging info message')
LOG.warning('This is a loggging warning message')
LOG.error('This is a loggging error message')
LOG.critical('This is a loggging critical message')

"""
"""
输出结果：
2021-09-04 11:03:13,549 - DEBUG - This is a loggging debug message
2021-09-04 11:03:13,549 - INFO - This is a loggging info message
2021-09-04 11:03:13,550 - WARNING - This is a loggging warning message
2021-09-04 11:03:13,550 - ERROR - This is a loggging error message
2021-09-04 11:03:13,550 - CRITICAL - This is a loggging critical message

"""
