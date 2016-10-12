# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TaobaoAskAroundItem(scrapy.Item):
    goods_name = scrapy.Field()
    goods_id = scrapy.Field()
    goods_url = scrapy.Field()
    category_id = scrapy.Field()
    shop_id = scrapy.Field()
    shop_master = scrapy.Field()
    comment_count = scrapy.Field()
    sale = scrapy.Field()
    shop_url = scrapy.Field()
    price = scrapy.Field()
    local = scrapy.Field()
    
    
    
     
