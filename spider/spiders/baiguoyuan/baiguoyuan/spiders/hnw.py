# encoding:utf8
"""
@File        : hnw.py
@Time        : 2019/6/20 16:30
@Author      : zhaoy
@Email       : zhaoyao@shandiangou.cc
@Description :  惠农网 爬虫
"""
import json

import pymongo
import scrapy

from .hnw_cateid import *
from ..settings import *


class HuiNongWangSpider(scrapy.Spider):
    name = 'hnw'
    allowed_domains = ['cnhnb.com']
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'Host': "truffle.cnhnb.com",
            'Accept': "*/*",
            'hn-app-id': "xapp",
            'osType': "xapp",
            'Accept-Language': "zh-cn",
            'Content-Type': "application/json",
            'access-token': "D0E28F9A8FEF4DBEA402FB6757FB1242",
            'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, "
                          "like Gecko) Mobile/14G60 MicroMessenger/7.0.3(0x17000321) NetType/WIFI Language/zh_CN",
            'Cache-Control': "no-cache",
            'accept-encoding': "gzip, deflate",
            'Connection': "keep-alive",
        },
        'IMAGES_STORE': 'G:/spiders_data/images/hnw/',
        'ITEM_PIPELINES': {
            'baiguoyuan.pipelines.GoodsImagesPipeline': 1,
            'baiguoyuan.pipelines.HnwPipelines': 324
        },
    }
    cate_list = 'https://truffle.cnhnb.com/banana/category/query/categories'
    supply_list = 'https://truffle.cnhnb.com/monk/esearch/supply/v2/list'
    base_image = 'https://image.cnhnb.com/'

    def __init__(self):
        self.client = pymongo.MongoClient(host=MONGO_URI)
        self.db = self.client[MONGO_DATABASE]
        self.collection = 'grids'
        super(HuiNongWangSpider, self).__init__()

    def start_requests(self):
        # cate_level_2 = self.db.get_collection('hmw_cate').find({}, {})
        # for cat in cate_level_2:
        #     url = ''
        # 目前只抓 农产品下的 水果 蔬菜 禽畜肉蛋 水产
        payload1 = {"codetype": "parentId", "code": None}
        for cat in cateId1.get('data')[0].get('data')[0:4]:
            payload1['code'] = cat.get('extraInfo')
            yield scrapy.Request(self.cate_list, callback=self.parse_cateid3, method='POST',
                                 body=json.dumps(payload1), meta={'payload1': payload1})

    def parse_cateid3(self, response):
        data = response.text
        data = json.loads(data)
        if data.get('data'):
            categorys = data.get('data').get('categorys')
            payload2 = {
                "id": "category",
                "keyword": "草莓",
                "cateId1": 2003191,
                "sfrom": 2,
                "pageNumber": 0,
                "num": 0,
                "cateId3": 2001325,
                "relateCate": False,
                "pageSize": 20
            }
            for cat in categorys:
                payload2['cateId3'] = cat.get('id')
                payload2['keyword'] = cat.get('name')

                yield scrapy.Request(self.supply_list, callback=self.page_up, method='POST',
                                     body=json.dumps(payload2), meta={'payload2': payload2})

    def page_up(self, response):
        """
        翻页
        :param response:
        :return: 发起新的请求
        """
        data = response.text
        data = json.loads(data)
        data = data.get('data')
        meta = response.meta
        if data:
            payload2 = meta.get('payload2')
            size = data.get('size')
            page_num = int((size)/20)
            for i in range(0, page_num):
                payload2['pageNumber'] = i
                yield scrapy.Request(self.supply_list, callback=self.parse_supply_list, method='POST',
                                     body=json.dumps(payload2))

    def parse_supply_list(self, response):
        data = response.text
        data = json.loads(data)
        data = data.get('data')
        if data:
            datas = data.get('datas')
            image_urls = [(self.base_image + dt.get('url400'), dt.get('cateName')) for dt in datas]
            data.update({'image_urls': image_urls})
            image_header = self.custom_settings.get('DEFAULT_REQUEST_HEADERS')
            image_header['Host'] = 'image.cnhnb.com'
            data.update({'image_header': image_header})
            yield data


