# -*- coding: utf-8 -*-

from conf import CrawlerSite

BOT_NAME = 'Scrapy'

SPIDER_MODULES = ['worker.crawler.Scrapy.spiders']
NEWSPIDER_MODULE = 'worker.crawler.Scrapy.spiders'

LOG_ENABLED = False

USER_AGENT = [('Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) '
               'Chrome/41.0.2228.0 Safari/537.36'),
              ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) '
               'Chrome/41.0.2227.1 Safari/537.36'),
              ('Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) '
               'Chrome/40.0.2214.93 Safari/537.36'),
              'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1',
              'Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0',
              'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; AS; rv:11.0) like Gecko',
              'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
              ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
               'Chrome/42.0.2311.135 Safari/537.36 Edge/12.246'),
              ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) '
               'Version/7.0.3 Safari/7046A194A'),
              ('User-Agent    Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/602.1.50 (KHTML, like Gecko) '
               'Version/10.0 Safari/602.1.50')]

DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
    'Upgrade-Insecure-Requests': 1,
    'DNT': 1,
    'Cache-Control': 'max-age=0'
}

REACTOR_THREADPOOL_MAXSIZE = 20

CONCURRENT_REQUESTS = CrawlerSite.CONCURRENT

CONCURRENT_REQUESTS_PER_DOMAIN = 32

CONCURRENT_ITEMS = 0

DOWNLOAD_DELAY = 0

DOWNLOAD_TIMEOUT = 15

COOKIES_ENABLED = False

RETRY_ENABLED = False

ROBOTSTXT_OBEY = False

HTTPCACHE_ENABLED = False

DOWNLOADER_MIDDLEWARES = {
    'worker.crawler.Scrapy.contrib.user_agent.CustomUserAgent': 500,
    'worker.crawler.Scrapy.contrib.proxy.ProxyMiddleware': 750,
}
