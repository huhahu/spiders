# -*- coding: utf-8 -*-
"""
社区人 爬虫
"""

import json

import pymongo
import scrapy

from .citys import shequren_city_info
from ..settings import *


class SheQuRen(scrapy.Spider):
    name = 'sqr'
    allowed_domains = ['shequren.cn']
    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'Host': "api.shequren.cn",
            'Content-Type': "application/json",
            'Accept-Encoding': "gzip, deflate",
            'Connection': "keep-alive",
            'Accept': "*/*",
            'User-Agent': "Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 "
                          "(KHTML, like Gecko) Mobile/14G60 MicroMessenger/7.0.3(0x17000321) NetType/WIFI Language/zh_CN",
            'Authorization': "Bearer AT-14056-cwu0hbVKXFjfe3CpnznayeOtnehErIiMbWT",
            'Accept-Language': "zh-cn",
            'Cache-Control': "no-cache",
        },
        'IMAGES_STORE': 'G:/spiders_data/images/sqr/',
        'ITEM_PIPELINES': {
            'baiguoyuan.pipelines.GoodsImagesPipeline': 1,
            'baiguoyuan.pipelines.SqrPipelines': 321
        },
    }

    def __init__(self):
        self.client = pymongo.MongoClient(host=MONGO_URI)
        self.db = self.client[MONGO_DATABASE]
        self.collection = 'grids'
        super(SheQuRen, self).__init__()

    def start_requests(self):
        bgy_citymap = {}
        [bgy_citymap.update({ct.get('name'): ct.get('cityCode')}) for ct in
         shequren_city_info.get('_embedded').get('content')]
        locations = self.db.get_collection(self.collection).find({'city': '西安市'},
                                                                 {'city': 1, 'center_lat': 1, 'center_lng': 1})
        url = 'https://api.shequren.cn/dmn/dominos/nearby?page=0&size=20&lat={lat}&lon={lon}&cityZone={code}'
        for loc in locations:
            cid = bgy_citymap.get(loc.get('city'))
            if cid:
                data = {
                    'lon': loc.get('center_lng'),
                    'lat': loc.get('center_lat'),
                    'code': cid,
                }
                ul = url.format(**data)
                yield scrapy.Request(ul, callback=self.parse_store_list)

    def parse_store_list(self, response):
        data = response.text
        data = json.loads(data)
        data.update({'data_type': 'sqr_stores'})
        yield data
        _data = data.get('_embedded')
        if _data:
            yield _data
            _data = _data.get('content')
            for dt in _data:
                dct = dict()
                dct['dmId'] = dt.get('id')
                for tp in [-1, 0, 1]:
                    dct['type'] = tp
                    url = 'https://api.shequren.cn/dmn/dominos/classify/goods?dmId={dmId}&type={type}&shareGid=0'
                    url = url.format(**dct)
                    yield scrapy.Request(url)
        else:
            return

    def parse(self, response):
        data = response.text
        data = json.loads(data)
        image_urls = []
        image_header = {
            'Host': "freshtank.oss-cn-zhangjiakou.aliyuncs.com",
            'Accept': "image/*;q=0.8",
            'Accept-Language': "zh-cn",
            'Connection': "keep-alive",
            'Accept-Encoding': "gzip, deflate",
            'Cache-Control': "no-cache",
        }
        if data:
            image_urls = [(item.get('image'), item.get('name')) for item in data]

        yield {'data_type': 'sqr_goods', 'data': data, 'image_urls': image_urls, 'image_header': image_header}
