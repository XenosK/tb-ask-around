#coding:utf-8
from scrapy.conf import settings
from scrapy.exceptions import IgnoreRequest

import atexit
import logging
import time
from pybloom import ScalableBloomFilter


logger = logging.getLogger('BloomMiddleware')
fh = logging.FileHandler('bloomlog')
logger.addHandler(fh)



class BloomMiddleware(object):

    logger.info('Creating Bloomfilter')
    
    try:
        bloom_file = open(settings['BLOOM_FILE'], 'rb')
    except:
        raise Exception('BLOOM_FILE ERROR')
        
    if settings['URL_FILE']:
        try:
            url_file = open(settings['URL_FILE'], 'r')
        except:
            raise Exception('URL_FILE ERROR')
        bloomfilter = ScalableBloomFilter(mode=ScalableBloomFilter.SMALL_SET_GROWTH)
        for x in url_file.read().split('\n'):
            bloomfilter.add(x)
        url_file.close()
    else: 
        bloomfilter = ScalableBloomFilter.fromfile(bloom_file)
    
    bloom_file.close()
    
    logger.info('Create Bloomfilter Complete')
    
   
    def __init__(self):
        #上次写入磁盘的时间点
        self.last_write_time = time.time()
        #写入磁盘的时间间隔(s)
        self.count = 0
        if not isinstance(settings['BLOOM_WRITE_TIME'], int):
            self.write_time = 300
        else:
            self.write_time = settings['BLOOM_WRITE_TIME']
        #在结束时将 bloomfilter 内容写入到磁盘
        atexit.register(self.write_to_disk)          
        
    def process_request(self, request, spider):
        #对有 Bloom 标记的 url 进行判重
        if request.meta.get('Bloom'):
            #如果 url 在 bloomfilter 中则丢弃这个 request
            tid= request.meta['item']['goods_id']
            #否则将 url 添加到 bloomfilter
            if tid in self.bloomfilter:
                self.count += 1
                logger.info('IGNORE Request [goods_id:%s] ' % tid)
                logger.info(self.count)
                raise IgnoreRequest
            else:
                logger.debug('[id:%s]not in bloom file' % tid)
                self.bloomfilter.add(tid)
                return None
        #定时将 bloomfilter 写入到磁盘
        if time.time() - self.last_write_time > self.write_time:
            self.last_write_time = time.time()
            self.write_to_disk()
        return None
        
    def write_to_disk(self):
        logger.info('WRITE TO DISK')
        save_file = open(settings['BLOOM_FILE'], 'wb')
        self.bloomfilter.tofile(save_file)
        save_file.close()
        logger.info('WRITE COMPLETE')
        
    
    
