#coding:utf-8
import scrapy
from taobao_ask_around.items import TaobaoAskAroundItem
import logging
import json
import re
import hashlib

logger = logging.getLogger(__name__)
fh = logging.FileHandler('log')
logger.addHandler(fh)

cat_dic = {'50102996':u'女装','16':u'女装/女士精品','50008165':u'童装/婴儿装/亲子装','1705':u'饰品/流行首饰/时尚饰品','50340020':u'流行女鞋','1625':u'女士内衣/男士内衣/家居服','50006843':u'女鞋','50344007':u'流行男装','30':u'男装','50006842':u'女包','50067081':u'孕妇装/孕产妇用品/营养','50010404':u'服饰配件/皮带/帽子/围巾','50016756':u'运动服/休闲服','50016853':u'男鞋/皮鞋/休闲鞋','50010388':u'运动鞋','50468016':u'运动鞋/休闲鞋','50072688':u'功能箱包','54164002':u'童鞋/婴儿鞋/亲子>鞋','50482014':u'运动服/休闲服装','50072686':u'男包','50484015':u'运动包/户外包/配件'}


class Ask(scrapy.Spider):
    name = 'ask'
    start_urls = ['https://s.taobao.com/search?data-key=cat&data-value=%s&ajax=true&sort=sale-desc' % x for x in cat_dic]

    def parse(self, response):
        try:
            result = json.loads(response.body)
        except:
            logger.error('[parse] json load response failed')
        # 获取response页数 
        now_page = response.meta.get('next_page')
        # 当前response的cat_id
        if not now_page:
             now_cat_id = re.findall(r'data-value=(\d+)', response.url)[0]
             logger.info('[parse] [cat_id: %s] not next' % now_cat_id)
        else:
             now_cat_id = re.findall(r'cat=(\d+)', response.url)[0]
             logger.info('[parse] [cat_id: %s] is next' % now_cat_id)
        #获取分类信息
        category = response.meta.get('category', {})
        if not category:
            try:
                # 没有分类信息的为start_urls的response
                category_level = '1'
                category_name = cat_dic[now_cat_id]
                category[category_level] = category_name
            except: 
                logger.info('[parse] set category failed')
                category = {'1':''}
        # 解析商品数据
        try:
            data_info_list = result['mods']['itemlist']['data']['auctions']
            logger.info('[parse] [cat_id: %s]parse the goods info' % now_cat_id)
        except:
            logger.error('[parse] [cat_id: %s] parse goods info failed' % now_cat_id)
            data_info_list = []
        for data_info_dic in data_info_list:
            item = TaobaoAskAroundItem()
            try:
                comment_count = data_info_dic['comment_count']
                if int(comment_count) < 20:
                    logger.debug('comment less %s' % comment_count)
                    continue
                item['goods_name'] = data_info_dic['title']
                item['goods_id'] = data_info_dic['nid']
                item['goods_url'] = data_info_dic['detail_url']
                item['category_id'] = data_info_dic['category']
                item['shop_id'] = data_info_dic['user_id']
                item['shop_master'] = data_info_dic['nick']                
                item['comment_count'] = comment_count
                item['sale'] = data_info_dic['view_sales']
                item['shop_url'] = data_info_dic['shopLink']
                item['price'] = data_info_dic['view_price']
                item['local'] = data_info_dic['item_loc']
                item['category'] = category
            except:
                logger.info('[parse] [cat_id: %s] fill the item faild, continue' % now_cat_id)
                continue
            # 根据商品id 获取问答对 在中间件生成url
            logger.debug('[parse] [goods_id:%s] create request' % item['goods_id'])
            yield scrapy.Request('http://tmp', callback=self.parse_ask, meta={'item':item, 'ask':True, 'Bloom':True}, dont_filter=True)
        # 略过翻页的response
        if not now_page:
            now_page = 0
        try:
            pager_info = result['mods']['pager']['data']
            page_size = int(pager_info['pageSize'])
            page_count = int(pager_info['totalPage'])
        except:
            page_count = 1
            logger.error('[parse] parse pager info failed')
        # 对当前商品搜索 翻页
        logger.info('[parse] [cat_id: %s] get next  page' % now_cat_id)
        # 防止request堆积太多 cookie失效 只翻一页
        if now_page < page_count:
            next_page = now_page + 1
            next_page_url = 'https://s.taobao.com/search?data-key=s&data-value=%s&ajax=true&cat=%s&sort=sale-desc' % (next_page * page_size, now_cat_id)
            yield scrapy.Request(next_page_url, callback=self.parse,  meta={'category':category,'next_page':next_page})
        # 未翻页的response
        if next_page == 0:
            # 找到下一级cat_id
            data_list = result['mods']['nav']['data'].get('common') 
            if data_list:
                logger.info('[parse] [cat_id: %s] get the sub cat id' % now_cat_id)
                sub_category_list= data_list[0]['sub']
                for sub_category_dic in sub_category_list:
                    name = sub_category_dic['text']
                    cat_id = sub_category_dic['value']
                    new_category = category.copy()
                    # 将提取出的类别加入category中
                    new_category[str(int(category.keys()[-1]) + 1)] = name
                    url = 'https://s.taobao.com/search?data-key=cat&data-value=%s&ajax=true&sort=sale-desc' % cat_id 
                    # 爬取新cat_id首页
                    yield scrapy.Request(url, callback=self.parse, meta={'category':new_category})


    def parse_ask(self, response):
        logger.info('[parse_ask]')
        item = response.meta['item']
        goods_id = item['goods_id']
        page = response.meta.get('page', 1)
        try:
            result = json.loads(response.body[9:-1])
        except:
            logger.info('[parse_ask] [id:%s]json loads response error' % goods_id)
            result = json.loads(re.findall(r'\(([\s\S]+)\)', response.body)[0])
        question_data = result['data']                   
        question_count = question_data['questCount']
        logger.info('[parse_ask] get question count: %s [goods_id:%s]' % (question_count, goods_id))
        question_cards = question_data.get('cards', None)
        # 防止request堆积太多导致cookie失效 翻一页 
        if page < int(question_count) / 10.0 :
            page += 1
            logger.info('[parse_ask] [id:%s] [page:%s]' % (goods_id, page))
            yield scrapy.Request('http://tmp', callback=self.parse_ask, meta={'item':item, 'ask':True, 'page':page}, cookies={'a':0}, dont_filter=True)
    
        if question_cards:
            logger.info('[parse_ask] [id:%s] get question cards success' % goods_id)
            '''
            ask_around_list =[
                {question:xx,
                 ask_time:xx,
                 topic_id:xx,
                 answer_list:[
                     {answer_time:x,
                      answer_feed:x,
                      answer_user:{x},
                      answer_vip:x,
                      answer:x},
                      ...,
                     {tmp_dic},
                 ]
                },
                ...,
                {ask_around_dic},
            ]
            '''
            ask_around_list = []
            for aq_dic in question_cards:
                ask_around_dic={}
                ask_around_dic['question'] = aq_dic['question']
                ask_around_dic['ask_time'] = aq_dic['gmtCreate']
                ask_around_dic['topic_id'] = aq_dic['topicId']
                answer_list = []
                for answer_dic in aq_dic.get('answers', []):
                    tmp_dic = {}  
                    tmp_dic['answer'] = answer_dic['desc']
                    tmp_dic['answer_time'] = answer_dic['createTime']
                    tmp_dic['answer_feed'] = answer_dic['feedId']
                    tmp_dic['answer_user'] = answer_dic['user']
                    tmp_dic['answer_vip'] = answer_dic['vipLevel']
                    answer_list.append(tmp_dic)                    
                ask_around_dic['answer_list'] = answer_list
                ask_around_list.append(ask_around_dic)
            item['ask_around_list'] = ask_around_list
            logger.info('[parse_ask] [id:%s] yield item' % goods_id)
            yield item
                

                
            
            


        
                
