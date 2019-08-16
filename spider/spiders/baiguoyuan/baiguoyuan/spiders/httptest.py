# -*- coding: utf-8 -*-
import json
import scrapy


class HttptestSpider(scrapy.Spider):
    name = 'httptest'
    allowed_domains = ['httpbin.org']
    start_urls = ['http://httpbin.org/get']

    def parse(self, response):
        print(response.text)
        yield json.loads(response.text)
