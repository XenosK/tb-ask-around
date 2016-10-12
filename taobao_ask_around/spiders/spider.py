#coding:utf-8
import scrapy
import json
import re


cat_dic = {'50102996':'女装','16':'女装/女士精品','50008165':'童装/婴儿装/亲子装','1705':'饰品/流行首饰/时尚饰品','50340020':'流行女鞋','1625':'女士内衣/男士内衣/家居服','50006843':'女鞋','50344007':'流行男装','30':'男装','50006842':'女包','50067081':'孕妇装/孕产妇用品/营养','50010404':'服饰配件/皮带/帽子/围巾','50016756':'运动服/休闲服','50016853':'男鞋/皮鞋/休闲鞋','50010388':'运动鞋','50468016':'运动鞋/休闲鞋','50072688':'功能箱包','54164002':'童鞋/婴儿鞋/亲子鞋','50482014':'运动服/休闲服装','50072686':'男包','50484015':'运动包/户外包/配件'}

#https://s.taobao.com/search?data-key=s&data-value=88&ajax=true&cat=16&sort=sale-desc
class Ask(scrapy.Spider):
    name = 'ask'
    start_urls = [ 
       'https://s.taobao.com/search?data-key=cat&data-value=%s&ajax=true&sort=sale-desc' % x for x in cat_dic]

    def parse(self, response):
        '''
        解析首页
        '''
        item = 
        result = json.loads(response.body)
        data_list = result['mods']['nav']['data'].get('common')
        # 请求成功即存在的cat_id
        now_cat_id = re.findall(r'data-value=(\d+)', response.url)
        # 判断类别等级，解析类别名称
        category_levle = response.meta.get('category_levle', 0)
        category_name = response.meta.get('category_name', '')
        if now_cat_id in cat_id:
            category_levle = 1
            category_name = cat_id['now_cat_id']
        # 找到下一级cat_id 
        if data_list:
            # 爬取新cat_id首页
            sub_category_list= data_list[0]['sub']
            for sub_category_dic in sub_category_list:
                name = sub_category_dic['text']
                cat_id = sub_category_dic['value']
                url = 'https://s.taobao.com/search?data-key=cat&data-value=%s&ajax=true&sort=sale-desc' % cat_id
                yield scrapy.Request(url, callback=self.parse,
                                      meta={'category_levle':category_levle + 1,'category_name':name})
        # 对 now_cat_id 翻一页
        next_page_url = 'https://s.taobao.com/search?data-key=s&data-value=44&ajax=true&cat=16&sort=sale-desc' % now_cat_id
        # 解析数据
        data = result['mods']['itemlist']['data']['auctions']
        
          







        yield scrapy.Request(next_page_url, callback=self.parse_page,
                               meta={'category_levle':category_levle, 'category_name':category_name})


    def parse_page(self, response):
        '''
        解析翻页
        '''
        pass
        
        
 
         
