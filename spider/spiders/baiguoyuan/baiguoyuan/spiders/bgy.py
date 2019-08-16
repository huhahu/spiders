# -*- coding: utf-8 -*-
"""
@File        : bgy_update.py
@Time        : 2019/6/17 10:32
@Author      : zhaoy
@Email       : zhaoyao@shandiangou.cc
@Description :  以经纬度栅格数据为基础，先抓 商铺数据， 再抓商品数据
特点 ： 由于要遍历栅格， 请求次数多， 抓一次需要的时间久.
"""

import copy
import json

import pymongo
import scrapy

from .citys import citys_info
from ..settings import *


class BgySpider(scrapy.Spider):
    name = 'bgy'
    allowed_domains = ['pagoda.com.cn']
    start_urls = ['http://pagoda.com.cn/']
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'Host': "pagoda-buy-acc.pagoda.com.cn:11521",
            'userToken': "",
            'cityID': "1",
            'X-DEFINED-appinfo': '''{"deviceID":"device2495146","os":"iOS 10.3.3",
                    "verCode":"3.3.2","model":"iPhone 6s Plus","channel":"AppStore","verName":"3.3.2.0"}''',
            'Accept': "*/*",
            'User-Agent': "PagodaBuy/3.3.2 (iPhone; iOS 10.3.3; Scale/3.00)",
            'Accept-Language': "zh-Hans-CN;q=1, zh-Hant-CN;q=0.9",
            'Accept-Encoding': "gzip, deflate",
            'Connection': "keep-alive",
            'cache-control': "no-cache"
        },
        'IMAGES_STORE': 'G:/spiders_data/bgy/images',
        'ITEM_PIPELINES': {
            'baiguoyuan.pipelines.GoodsImagesPipeline': 1,
            'baiguoyuan.pipelines.BgyPipeline': 320,
        }
    }

    data = {
        'cityID': '1',
        'lon': '114.180515',
        '_appInfo': {'verName': '3.3.2.0', 'deviceID': 'device2495146', 'os': 'iOS 10.3.3', 'verCode': '3.3.2',
                     'model': 'iPhone 6s Plus', 'channel': 'AppStore'},
        'lat': '22.566535',
        'isSupportTake': '',
        'cityName': '深圳市'
    }

    def __init__(self):

        self.client = pymongo.MongoClient(host=MONGO_URI)
        self.db = self.client[MONGO_DATABASE]
        self.collection = 'grids'
        super(BgySpider, self).__init__()

    def start_requests(self):
        headers = self.custom_settings.get('DEFAULT_REQUEST_HEADERS')
        bgy_citymap = {}
        [bgy_citymap.update({ct.get('name'): ct.get('cityID')}) for ct in citys_info]
        locations = self.db.get_collection(self.collection).find({'city': {'$nin': ['深圳市', '昆明市']}}, {'city': 1, 'center_lat': 1, 'center_lng': 1})
        url = 'https://pagoda-buy-acc.pagoda.com.cn:11521/api/v1/city/listStore'
        for loc in locations:
            bgy_cityid = bgy_citymap.get(loc.get('city'))
            if bgy_cityid:
                data = self.data
                data['lon'] = loc.get('center_lng')
                data['lat'] = loc.get('center_lat')
                data['cityName'] = loc.get('city')
                data['cityID'] = bgy_cityid
                print(data)
                header = copy.deepcopy(headers)
                header['cityID'] = bgy_cityid
                yield scrapy.Request(url, callback=self.parse_store_list, method='POST', headers=header,
                                     body=json.dumps(data))

    def parse_store_list(self, response):
        data = response.text
        data = json.loads(data)
        data.update({'data_type': 'bgy_stores'})
        print(data)
        yield data
        data = data.get('data')
        if data:
            headers = self.custom_settings.get('DEFAULT_REQUEST_HEADERS')
            for dt in data:
                cityid = dt.get('cityID')
                storeid = dt.get('storeID')
                cityname = dt.get('cityName')
                header = copy.deepcopy(headers)
                header['cityID'] = dt.get('cityID')
                meta = {'store_id': storeid, 'city_id': cityid, 'city': cityname}
                url = '''https://pagoda-buy-acc.pagoda.com.cn:11521
                                /api/v1/category/goods/-1/''' + cityid + '''/''' + str(storeid) + '''/13?_appInfo%5Bchannel
                                %5D=AppStore&_appInfo%5BdeviceID%5D=device2495146&
                                _appInfo%5Bmodel%5D=iPhone%206s%20Plus&_appInfo
                                %5Bos%5D=iOS%2010.3.3&_appInfo%5BverCode%5D=3.3.2
                                &_appInfo%5BverName%5D=3.3.2.0'''
                yield scrapy.Request(url, headers=header, meta=meta)
        else:
            return

    def parse(self, response):
        meta = response.meta
        meta['data_type'] = 'bgy_goods'
        data = response.text
        data = json.loads(data)
        data.update(meta)
        image_urls = [item.get('image') for item in data.get('data')]
        data.update({'image_urls': image_urls})
        yield data
