# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class StocksItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    bonuse = scrapy.Field()


class HKBuyStock(scrapy.Item):
    code = scrapy.Field()
    name = scrapy.Field()
    shareholding = scrapy.Field()
    shareholding_percent = scrapy.Field()
    date = scrapy.Field()
    uuid = scrapy.Field()
