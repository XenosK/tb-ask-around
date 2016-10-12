#coding:utf-8
import scrapy
from taobao_ask_around.items import TaobaoAskAroundItem
import logging
import json
import re
import hashlib

logger = logging.getLogger(__name__)

cat_dic = {'50102996':u'女装','16':u'女装/女士精品','50008165':u'童装/婴儿装/亲子装','1705':u'饰品/流行首饰/时尚饰品','50340020':u'流行女鞋','1625':u'女士内衣/男士内衣/家居服','50006843':u'女鞋','50344007':u'流行男装','30':u'男装','50006842':u'女包','50067081':u'孕妇装/孕产妇用品/营养','50010404':u'服饰配件/皮带/帽子/围巾','50016756':u'运动服/休闲服','50016853':u'男鞋/皮鞋/休闲鞋','50010388':u'运动鞋','50468016':u'运动鞋/休闲鞋','50072688':u'功能箱包','54164002':u'童鞋/婴儿鞋/亲子>鞋','50482014':u'运动服/休闲服装','50072686':u'男包','50484015':u'运动包/户外包/配件'}


class Ask(scrapy.Spider):
    name = 'ask'
    start_urls = [ 
       'https://s.taobao.com/search?data-key=cat&data-value=%s&ajax=true&sort=sale-desc' % x for x in cat_dic]

    def parse(self, response):
        '''
        解析首页
        '''
        item = TaobaoAskAroundItem()
        result = json.loads(response.body)
        data_list = result['mods']['nav']['data'].get('common')
        # 请求成功即存在的cat_id
        now_cat_id = re.findall(r'data-value=(\d+)', response.url)[0]
        # 判断类别等级，解析类别名称
        category = response.meta.get('category', {})
        if now_cat_id in cat_dic:
            category_level = 1
            category_name = cat_dic[now_cat_id]
            category[category_level] = category_name
        print '==================================', category
        # 找到下一级cat_id 
        if data_list:
            sub_category_list= data_list[0]['sub']
            for sub_category_dic in sub_category_list:
                name = sub_category_dic['text']
                cat_id = sub_category_dic['value']
                # 增加类别 key 递增一个
                category[category.keys()[-1] + 1] = name
                url = 'https://s.taobao.com/search?data-key=cat&data-value=%s&ajax=true&sort=sale-desc' % cat_id 
                # 爬取新cat_id首页
                yield scrapy.Request(url, callback=self.parse,  meta={'category':category})

        # 解析商品数据
        data_info_list = result['mods']['itemlist']['data']['auctions']
        for data_info_dic in data_info_list:
            item['goods_name'] = data_info_dic['title'] 
            item['goods_id'] = data_info_dic['nid'] 
            item['goods_url'] = data_info_dic['detail_url'] 
            item['category_id'] = data_info_dic['category']
            item['shop_id'] = data_info_dic['user_id'] 
            item['shop_master'] = data_info_dic['nick'] 
            item['comment_count'] = data_info_dic['comment_count'] 
            item['sale'] = data_info_dic['view_sales'] 
            item['shop_url'] = data_info_dic['shopLink'] 
            item['price'] = data_info_dic['view_price'] 
            item['local'] = data_info_dic['item_loc']
            item['category'] = category

            # 根据商品id 获取问答对
            yield scrapy.Request('http://tmp', callback=self.parse_ask, meta={'item':item, 'ask':True})

        # 对 now_cat_id 翻页
        for page in range(1, 100):
            next_page_url = 'https://s.taobao.com/search?data-key=s&data-value=%s&ajax=true&cat=%s&sort=sale-desc'\
                               % (page * 44, now_cat_id)
            yield scrapy.Request(next_page_url, callback=self.parse_page,  meta={'category':category})


    def parse_page(self, response):
        '''
        解析翻页
        '''
        item = TaobaoAskAroundItem()
        category = response.meta['category']
        result = json.loads(response.body)
        data_info_list = result['mods']['itemlist']['data']['auctions']
        for data_info_dic in data_info_list:
            item['goods_name'] = data_info_dic['title']
            item['goods_id'] = data_info_dic['nid']
            item['goods_url'] = data_info_dic['detail_url']
            item['category_id'] = data_info_dic['category']
            item['shop_id'] = data_info_dic['user_id']
            item['shop_master'] = data_info_dic['nick']
            item['comment_count'] = data_info_dic['comment_count']
            item['sale'] = data_info_dic['view_sales']
            item['shop_url'] = data_info_dic['shopLink']
            item['price'] = data_info_dic['view_price']
            item['local'] = data_info_dic['item_loc']
            item['category'] = category

            # 根据商品id 获取问答对
            yield scrapy.Request('http://tmp', callback=self.parse_ask, meta={'item':item, 'ask':True})
 
    def parse_ask(self, response):
        pass


        
                
