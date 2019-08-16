# encoding:utf8
"""
@File        : bgy_update.py
@Time        : 2019/6/17 10:32
@Author      : zhaoy
@Email       : zhaoyao@shandiangou.cc
@Description :  遍历 bgy_stores 下的所有店铺 抓取商品数据
特点： 直接遍历店铺历史数据，请求次数少， 抓取速度快
"""

import copy
import json

import pymongo
import scrapy

from ..settings import *


class BgySpider(scrapy.Spider):
    base_image_url = 'https://oh6dt6vbt.qnssl.com'
    name = 'bgy_update'
    allowed_domains = ['pagoda.com.cn', 'https://oh6dt6vbt.qnssl.com']
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
        'IMAGES_STORE': 'G:/spiders_data/images/bgy/',
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
        self.collection = 'bgy_stores'
        super(BgySpider, self).__init__()

    def start_requests(self):
        headers = self.custom_settings.get('DEFAULT_REQUEST_HEADERS')
        stores = self.db.get_collection(self.collection).find({}, {'storeID': 1, 'cityID': 1, 'cityName': 1})
        for sd in stores:
            cityid = sd.get('cityID')
            cityname = sd.get('cityName')
            storeid = sd.get('storeID')
            header = copy.deepcopy(headers)
            header['cityID'] = cityid
            meta = {'store_id': storeid, 'city_id': cityid, 'city': cityname}
            url = '''https://pagoda-buy-acc.pagoda.com.cn:11521
                                            /api/v1/category/goods/-1/''' + cityid + '''/''' + str(storeid) + '''/13?_appInfo%5Bchannel
                                            %5D=AppStore&_appInfo%5BdeviceID%5D=device2495146&
                                            _appInfo%5Bmodel%5D=iPhone%206s%20Plus&_appInfo
                                            %5Bos%5D=iOS%2010.3.3&_appInfo%5BverCode%5D=3.3.2
                                            &_appInfo%5BverName%5D=3.3.2.0'''
            yield scrapy.Request(url, headers=header, meta=meta)

    def parse(self, response):
        meta = response.meta
        meta['data_type'] = 'bgy_goods'
        data = response.text
        data = json.loads(data)
        data.update(meta)
        if data.get('data'):
            image_urls = [(self.base_image_url + item.get('headPic'), item.get('goodsName')) for item in data.get('data')]
            data.update({'image_urls': image_urls})
            data.update({'image_header': {
                'Host': "oh6dt6vbt.qnssl.com",
                'Accept': "image/*;q=0.8",
                'Accept-Language': "zh-cn",
                'Connection': "keep-alive",
                'Accept-Encoding': "gzip, deflate",
                'User-Agent': "PagodaBuy/3.3.2.0 CFNetwork/811.5.4 Darwin/16.7.0",
                'Cache-Control': "no-cache",
            }})
        yield data
