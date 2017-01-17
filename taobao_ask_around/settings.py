# -*- coding: utf-8 -*-
BOT_NAME = 'taobao_ask_around'
SPIDER_MODULES = ['taobao_ask_around.spiders']
NEWSPIDER_MODULE = 'taobao_ask_around.spiders'
BLOOM_FILE = 'bloom'
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2146.0 Safari/537.36'
DEPTH_PRIORITY = 1 
SCHEDULER_DISK_QUEUE = 'scrapy.squeues.PickleFifoDiskQueue'
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeues.FifoMemoryQueue'
ROBOTSTXT_OBEY = False
#LOG_LEVEL = 'INFO'
CONCURRENT_REQUESTS = 16
DOWNLOAD_DELAY = 0.3
DEFAULT_REQUEST_HEADERS = {
   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
   'Accept-Language': 'ch-ZN',
}
DOWNLOADER_MIDDLEWARES = {
    'taobao_ask_around.addcookie.AddCookieMiddleware': 998,
     'taobao_ask_around.bloommidware.BloomMiddleware': 10,
}
ITEM_PIPELINES = {
    'taobao_ask_around.pipelines.TaobaoAskAroundPipeline': 300,
}

