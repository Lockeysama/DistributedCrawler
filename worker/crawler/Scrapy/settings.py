# -*- coding: utf-8 -*-

BOT_NAME = 'Scrapy'

SPIDER_MODULES = ['worker.crawler.Scrapy.spiders']
NEWSPIDER_MODULE = 'worker.crawler.Scrapy.spiders'

# LOG_LEVEL = 'INFO'

USER_AGENT = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_0) '
              'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36')

CONCURRENT_REQUESTS = 16

DOWNLOAD_DELAY = 0.5

# CONCURRENT_REQUESTS_PER_DOMAIN = 16

CONCURRENT_REQUESTS_PER_IP = 16

DOWNLOAD_TIMEOUT = 10

COOKIES_ENABLED=False

RETRY_ENABLED=False

DOWNLOADER_MIDDLEWARES = {
    'worker.crawler.Scrapy.contrib.user_agent.CustomUserAgent': 543,
    'worker.crawler.Scrapy.contrib.proxy.ProxyMiddleware': 480,
}

# EXTENSIONS = {
#     'scrapy_jsonrpc.webservice.WebService': 500,
# }
# 
# JSONRPC_ENABLED = True
# 
# JSONRPC_PORT = [6080]