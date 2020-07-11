import scrapy
import logging
import json

from scrapy import FormRequest

from stocks.items import HKBuyStock


class MySpider1(scrapy.Spider):
    name = 'northCapital'

    def __init__(self, *args, **kwargs):
        super(MySpider1, self).__init__(*args, **kwargs)

    def start_requests(self):
        url = 'https://www.hkexnews.hk/sdw/search/mutualmarket_c.aspx?t=sh&t=sh'
        form = {
            "__VIEWSTATE": "/wEPDwUJNjIxMTYzMDAwZGQ79IjpLOM+JXdffc28A8BMMA9+yg==",
            "__VIEWSTATEGENERATOR": "EC4ACD6F",
            "__EVENTVALIDATION": "/wEdAAdtFULLXu4cXg1Ju23kPkBZVobCVrNyCM2j+bEk3ygqmn1KZjrCXCJtWs9HrcHg6Q64ro36uTSn/Z2SUlkm9HsG7WOv0RDD9teZWjlyl84iRMtpPncyBi1FXkZsaSW6dwqO1N1XNFmfsMXJasjxX85jz8PxJxwgNJLTNVe2Bh/bcg5jDf8=",
            "today": "20200710",
            "sortBy": "stockcode",
            "sortDirection": "asc",
            "alertMsg": "",
            "txtShareholdingDate": "2020/06/10",
            "btnSearch": ""
        }
        yield FormRequest(url=url,
                             callback=self.parse,
                             formdata=form)

    def parse(self, response):
        stock_table = response.xpath('//table[@id="mutualmarket-result"]/tbody/tr[not(contains(@class,"thread"))]')
        for line in stock_table:
            item = HKBuyStock()
            code_expression = 'td[@class="col-stock-code"]/div[@class="mobile-list-body"]/text()'
            item['code'] = line.xpath(code_expression).extract()
            name_expression = 'td[@class="col-stock-name"]/div[@class="mobile-list-body"]/text()'
            item['name'] = line.xpath(name_expression).extract()
            shareholding_expression = 'td[@class="col-shareholding"]/div[@class="mobile-list-body"]/text()'
            item['shareholding'] = line.xpath(shareholding_expression).extract()
            shareholding_percent_expression = \
                'td[@class="col-shareholding-percent"]/div[@class="mobile-list-body"]/text()'
            item['shareholding_percent'] = line.xpath(shareholding_percent_expression).extract()
            logging.info("get one stock: %s, %s, %s, %s",
                         item['code'], item['name'], item['shareholding'], item['shareholding_percent'])
            yield item
        pass
