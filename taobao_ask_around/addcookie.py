#coding:utf-8
import logging
import hashlib
import json
import time
import urllib
import urllib2
import re

logger = logging.getLogger(__name__)
fh = logging.FileHandler('cookielog')
logger.addHandler(fh)

class AddCookieMiddleware(object):

    def __init__(self):
        # cookie 使用时间限制(s)
        self.cookie_time_limit = 600
        # cokie 使用次数限制
        self.cookie_use_times_limit = 100
        # 上次获取cookie的的时间点
        self.cookie_time = 0
        # 当前 cookie 使用次数
        self.cookie_use_times = 0
        self.first = True
        self.cookie = ''
        self.cookie = ''
        self.url = 'https://api.m.taobao.com/h5/mtop.taobao.ocean.quest.list.pc/1.0/?appKey=12574478&t=%s&sign=%s&api=mtop.taobao.ocean.quest.list.pc&v=1.0&type=jsonp&dataType=jsonp&data=%s'

    def process_request(self, request, spider):
        # 找到问答相关request, 并过滤掉已经生成url的request
        if request.meta.get('ask') and not request.meta.get('my_filter'):
            # 首次经过中间件 请求cookie
            if self.first:
                self.get_cookie()
            # 检测cookie时间
            self.check_time()
            # 检测cookie次数
            self.check_use_times()
            item = request.meta['item']
            goods_id = item['goods_id']
            logger.debug('[request] [id:%s] get ask_around request' % goods_id)
            #翻页的加上 "cursor":"页数"
            page = request.meta.get('page')
            if page:
                data = '{"itemId":"%s","cursor":"%s"}' % (item['goods_id'], page)
                logger.debug('[request] [id:%s] [page: %s]' % (goods_id, page))
            else:
                data = '{"itemId":"%s"}' % item['goods_id']

            try:
                url = self.create_url(data, self.cookie) 
            except:
                logger.error('[request] create url failed, reprocess the request')
                return request
            logger.debug('[request] [id:%s] create url' % goods_id)
            new_request = request.replace(url=url, cookies={'_m_h5_tk': self.cookie, '_m_h5_tk_enc':self.cookie1}, dont_filter=False)
            new_request.meta['my_filter'] = True
            self.cookie_use_times += 1
            return new_request

    def process_response(self, request, response, spider):
        if request.meta.get('ask'):
            #请求不成功
            retcode = response.headers['M-Retcode'] 
            if retcode != 'SUCCESS': 
                logger.warn('[%s] get response faild' % retcode)
                logger.info('reset the cookies')
                '''
                出错要不要重置cookie？
                cookie_list = response.headers.getlist('Set-cookie')
                if len(cookie_list) != 2:
                    logger.warn('get cookie failed, use [get_cookie]')
                    self.get_cookie()
                    return request 
                self.cookie = parse_cookie(cookie_list[0])
                self.cookie1 = parse_cookie1(cookie_list[1])
                '''
                return request 
        return response

    def create_url(self, data, cookie):
        q_data = self.quote_data(data)
        token = cookie.split('_')[0]     
        now = str(time.time()).replace('.', '')
        data_md5 = hashlib.md5()
        data_md5.update('%s&%s&12574478&%s' % (token, now, data))
        sign = data_md5.hexdigest()
        return self.url % (now, sign, q_data)        

    def quote_data(self, data):
        return urllib.quote(data)

    def parse_cookie(self, cookie):
        if cookie == '':
            logger.info('cookie is none')
            return 0
        return re.findall(r'_m_h5_tk=(.*?);', cookie)[0]
    
    def parse_cookie1(self, cookie):
        if cookie == '':
            return 0
        return re.findall(r'_m_h5_tk_enc=(.*?);', cookie)[0]

    def get_cookie(self):
        if self.first:
            logger.info('[get_cookie] first start up, get the cookie')
        logger.info('[get_cookie] get the cookie')
        url = 'https://api.m.taobao.com/h5/mtop.taobao.ocean.quest.list.pc/1.0/?appKey=12574478&t=147645292563&sign=50f374892cc03c718a4798db720f85c3&api=mtop.taobao.ocean.quest.list.pc'
        try:
            response = urllib2.urlopen(url)
        except:
            logger.info('[get_cookie] get response faild')
            logger.info('[get_cookie] try get cookie again')
            self.get_cookie()
        logger.info('[get_cookie] get cookie success')
        cookies = response.headers['set-cookie']
        self.cookie = self.parse_cookie(cookies)
        self.cookie1 = self.parse_cookie1(cookies)
        self.cookie_time = time.time()
        self.cookie_use_times = 0       
        self.first = False
    
    def check_time(self):
        if time.time() - self.cookie_time > self.cookie_time_limit:
            logger.info('over time limit, change the cookies')
            self.get_cookie()

    def check_use_times(self):
        if self.cookie_use_times > self.cookie_use_times_limit:
            logger.info('over use limit, change the cookies')
            self.get_cookie()


