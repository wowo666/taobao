# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json


class TaobaoPipeline(object):
    def process_item(self, item, spider):
        str_data = json.dumps(dict(item), ensure_ascii=False) + '\n'
        self.file.write(str_data)
        return item

    def __init__(self):
        self.file = open('taobao.txt', 'w', encoding='utf-8')

    def close_spider(self, spider):
        self.file.close()
