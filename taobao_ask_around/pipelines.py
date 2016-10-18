# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
from taobao_ask_around.items import TaobaoAskAroundItem
from pymongo import MongoClient

class TaobaoAskAroundPipeline(object):

    def __init__(self):
        client = MongoClient('192.168.1.234', 27017)
        db = client.Taobao
        self.collection = db.ask_r_20161018

    def process_item(self, item, spider):
        self.collection.insert(dict(item))
        return item
