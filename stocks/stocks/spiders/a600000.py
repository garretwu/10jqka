# -*- coding: utf-8 -*-
import scrapy
import logging


class MySpider(scrapy.Spider):
    name = 'stock'
    #start_urls = ['http://basic.10jqka.com.cn/600000/bonus.html']
    Schema = ['报告期', '董事会日期', '预案公告日期', '实施公告日', '分红方案说明', 'A股股权登记日', 'A股除权除息日', '分红总额',
              '方案进度', '股利支付率', '税前分红率']

    def __init__(self, code=600000, *args, **kwargs):
        super(MySpider, self).__init__(*args, **kwargs)
        self.code = code

    def start_requests(self):
        url = 'http://basic.10jqka.com.cn/%s/bonus.html' % self.code
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        bonus_table = response.xpath('//table[@id="bonus_table"]/tbody/tr[not(contains(@class,"thread"))]')

        for line in bonus_table:
            bonus_dict = {}
            for index in range(len(self.Schema)):
                expression = 'td[%d]//text()' % (index + 1)

                bonus_dict[self.Schema[index]] = line.xpath(expression).extract()[0]
            logging.info("get one dict: %s", bonus_dict)
            yield bonus_dict

