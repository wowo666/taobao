# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class TaobaoItem(scrapy.Item):
    # define the fields for your item here like:
    # 1.店铺名字
    商店名称 = scrapy.Field()
    # 2.店铺种类的名字
    商店种类 = scrapy.Field()
    # 3.店铺链接
    商店链接 = scrapy.Field()
    # 4.商品名称
    商品名称 = scrapy.Field()
    # 5.商品链接
    商品链接 = scrapy.Field()
    # 6.商品价格
    原价 = scrapy.Field()
    # 7.商品促销价
    促销价 = scrapy.Field()
    # 8.商品的人气
    人气 = scrapy.Field()
    # 9.商品的月销售量
    月销量 = scrapy.Field()
    pass
