# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re
import time

import pymongo
import scrapy
from scrapy.pipelines.images import ImagesPipeline


class MongoPipeline(object):
    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        pass


class BgyPipeline(MongoPipeline):
    collection_1 = 'bgy_stores'
    collection_2 = 'bgy_goods'

    def process_item(self, item, spider):
        print("enter pipeline")
        data_type = item.get('data_type')
        # 店铺列表
        if data_type == self.collection_1:
            data = item.get('data')
            if data:
                [dt.update(
                    {
                        'crawl_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    }
                ) for dt in data]
                print("enter pipeline")
                self.db.get_collection(self.collection_1).insert_many(data)
            return item

        # 商品列表
        if data_type == self.collection_2:
            data = item.get('data')
            if data:
                [dt.update(
                    {
                        'city': item.get('city'),
                        'city_id': item.get('city_id'),
                        'store_id': item.get('store_id'),
                        'crawl_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    }
                ) for dt in data]
                print(data)
                self.db.get_collection(self.collection_2).insert_many(data)
            return item


class SqrPipelines(MongoPipeline):
    collection_1 = 'sqr_stores'
    collection_2 = 'sqr_goods'

    def process_item(self, item, spider):
        data_type = item.get('data_type')
        # 店铺列表
        if data_type == self.collection_1:
            data = item.get('_embedded')
            if data:
                data = data.get('content')
                [dt.update(
                    {
                        'crawl_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    }
                ) for dt in data]
                self.db.get_collection(self.collection_1).insert_many(data)
            return item

        # 商品列表
        if data_type == self.collection_2:
            data = item.get('data')
            if data:
                [dt.update(
                    {
                        'crawl_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    }
                ) for dt in data]
                self.db.get_collection(self.collection_2).insert_many(data)
            return item


class HnwPipelines(MongoPipeline):
    collection_1 = 'hnw_goods'

    def process_item(self, item, spider):
        data = item.get('data')
        if data:
            datas = data.get('datas')
            [dt.update(
                {
                    'crawl_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                }
            ) for dt in datas]
            self.db.get_collection(self.collection_1).insert_many(datas)
        return item


class GoodsImagesPipeline(ImagesPipeline):
    collection_1 = 'goods_images'

    def __init__(self, store_uri, download_func=None, settings=None, mongo_uri=None, mongo_db=None):
        super(GoodsImagesPipeline, self).__init__(store_uri, download_func, settings)
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[mongo_db]

    @classmethod
    def from_settings(cls, settings):
        store_uri = settings['IMAGES_STORE']
        mongo_uri = settings['MONGO_URI']
        mongo_db = settings['MONGO_DATABASE']

        return cls(store_uri, settings=settings, mongo_uri=mongo_uri, mongo_db=mongo_db)

    def get_media_requests(self, item, info):
        headers = item.get('image_header')
        if item.get('image_urls'):
            for image_url, image_name in item['image_urls']:
                yield scrapy.Request(image_url, headers=headers, meta={'image_name': image_name})

    def item_completed(self, results, item, info):
        data = [x for ok, x in results if ok]
        if data:
            try:
                self.db.get_collection(self.collection_1).insert_many(data)
            except Exception as e:
                print(e)
        return item

    def file_path(self, request, response=None, info=None):
        image_fname = re.findall(r'.*/(.*\.[a-z]+)', request.url)
        image_fname = image_fname[0]
        image_name = request.meta['image_name']
        image_name = re.sub(r'[？\\*|“<>:/]', '', image_name)
        filename = u'{0}/{1}'.format(image_name, image_fname)
        return filename
