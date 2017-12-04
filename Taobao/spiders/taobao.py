# -*- coding: utf-8 -*-
import scrapy
from Taobao.items import TaobaoItem
import re
import time
import json
import copy
from urllib import request
# 此淘宝项目 难点在于寻找接口，以及商品数据接口参数需要url编码
# 没有用ip代理池，所以设置了随机延迟时间
# 有部分页面会有301,302重定向，所以使用redirect_enabled = False  不进行重定向

class TaobaoSpider(scrapy.Spider):
    name = 'taobao'
    # 翻页
    page = 1
    # 翻页
    k = 0
    # 所有店铺列表
    all_shop_list = []
    allowed_domains = ['taobao.com']
    start_urls = ['https://shopsearch.taobao.com/search?app=shopsearch']

    def parse(self, response):
        # 获取12种热门种类
        shop_type_name = re.findall(r'{"name":"(\S+?)"', response.text)
        # 创建对象
        item = TaobaoItem()
        llist = [n * 6 for n in range(12)]
        i = 0
        for n in range(len(shop_type_name)):
            if i in llist:
                item['商店种类'] = shop_type_name[n]
                url = 'https://shopsearch.taobao.com/search?data-key=s&data-value=0&ajax=true&_ksTS=1511058139704_756&app=shopsearch&spm=a230r.7195193.0.0.9l0Tsy&q=%s' % (item['商店种类'])
                time.sleep(0.01)
                yield scrapy.Request(url, callback=self.parse_shop_type_detail, meta={'meta_1': copy.deepcopy(item)})
                time.sleep(1)
            i += 1

    def parse_shop_type_detail(self, response):
        item = response.meta["meta_1"]
        # 从此种类下店铺接口  获取数据
        shop_name_list = json.loads(response.text)["mods"]["shoplist"]["data"]["shopItems"]
        # 进行遍历 获取数据
        for shop_name in shop_name_list:
            item['商店名称'] = shop_name['title']
            item['商店链接'] = shop_name['shopUrl']
            # 去除重复的店铺
            if item['商店链接'] not in self.all_shop_list:
                # 将商店添加到遍历过的列表
                self.all_shop_list.append(item['商店链接'])
                # 此接口为获取商店下所有商品的接口  参数为商店的url
                url = 'https:%s/i/asynSearch.htm?mid=w-15615345423-0&search=y&pageNo=1' % (item['商店链接'])
                yield scrapy.Request(url, callback=self.parse_shop_detail, meta={"item": copy.deepcopy(item)})
        # 每种热门种类下只能找到5000家
        while self.k < 4980:
            # 每页显示20家商店， 每次参数增加20
            self.k += 20
            # 下一页的链接
            next_url = 'https://shopsearch.taobao.com/search?data-key=s&data-value=%s&ajax=true&_ksTS=1511058139704_756&app=shopsearch&spm=a230r.7195193.0.0.9l0Tsy&q=%s' % (self.k, item['商店名称'])
            yield scrapy.Request(next_url, callback=self.parse_shop_type_detail, meta={'meta_1': copy.deepcopy(item)})

    def parse_shop_detail(self, response):
        item = response.meta["item"]
        # 获取所有商品的数据
        goods_list = response.xpath('/html/body/div/div[2]/div/dl/dd[1]/a')
        # 进行遍历
        for goods in goods_list:
            item['商品名称'] = goods.xpath('./text()').extract()[0].replace('                                        ', '')
            item['商品链接'] = goods.xpath('./@href').extract()[0].replace(r'\"', '')
            # url = 'https:' + item['goods_url']
            # 商品的id
            goodsid = int(re.findall('id=(\d+)', item['商品链接'])[0])
            # 此为商品的数据接口的参数
            canshu = '{"exParams":"{\"countryCode\":\"CN\",\"phoneType\":\"iPhone7,2\",\"itemId\":\"%s\",\"item_id\":\"%s\"}","itemNumId":"%s","detail_v":"3.1.0"}' % (
            goodsid, goodsid, goodsid)
            # 需要将参数进行URL编码
            url_e = request.quote(canshu, encoding='UTF-8')
            # 再参数输入
            url = 'https://trade-acs.m.taobao.com/gw/mtop.taobao.detail.getdetail/6.0?rnd=524D0EB5FC9F4A909BA3A7B089D7B947&data=%s' % url_e
            yield scrapy.Request(url, callback=self.parse_goods_detail, meta={"item": copy.deepcopy(item)})
        # 捕捉无数据才有的数据， 无异常不翻页，有异常没匹配成功 即还有数据，继续翻页
        try:
            response.xpath('/html/body/div/div[2]/p/strong/text()')
        except:
            self.page += 1
            next_url = 'https:%s/i/asynSearch.htm?mid=w-15615345423-0&search=y&pageNo=%s' % (item['商店链接'], self.page)
            yield scrapy.Request(next_url, callback=self.parse_shop_detail, meta={"item": copy.deepcopy(item)})

    def parse_goods_detail(self, response):
        item = response.meta["item"]
        time.sleep(1)
        # 此页面含有大量数据，每个商店都有不同的不显示数据，所以有很多try
        try:
            item['月销量'] = re.findall(r'\\"sellCount\\":\\"(\d+)\\', response.text)[0]
        except:
            item['月销量'] = '此店不显示销售量'
        item['人气'] = re.findall(r'"favcount":"(\d+)"', response.text)[0]
        try:
            item['促销价'] = re.findall(r'\\"price\\":{\\"priceText\\":\\"(.*?)\\"', response.text)[0]
        except:
            item['促销价'] = '无促销'
        try:
            item['原价'] = re.findall(r'extraPrices\\":\[{\\"priceText\\":\\"(.*?)\\', response.text)[0]
        except:
            try:
                item['原价'] = re.findall(r'\\"extraPrices\\":\[{\\"priceMoney\\":\\".*?\\",\\"priceText\\":\\"(.*?)\\"', response.text)[0]
            except:
                item['原价'] = item['促销价']
                item['促销价'] = '无促销'
        finally:
            yield item
