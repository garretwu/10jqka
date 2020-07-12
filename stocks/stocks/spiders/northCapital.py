import uuid
import scrapy
import logging

from scrapy import FormRequest
from stocks.items import HKBuyStock
from datetime import date
from datetime import timedelta


class NorthCapital(scrapy.Spider):
    name = 'northCapital'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.startDate is None:
            self.startDate = date.today()
        else:
            self.startDate = date.fromisoformat(self.startDate)
        self.currentDate = self.startDate
        if self.duration is None:
            self.duration = 1
        self.endDate = self.startDate + timedelta(days=int(self.duration))
        self.dateSet = set()

    def start_requests(self):
        url = 'https://www.hkexnews.hk/sdw/search/mutualmarket_c.aspx?t=sh&t=sh'
        form = {
            "__VIEWSTATE": "/wEPDwUJNjIxMTYzMDAwZGQ79IjpLOM+JXdffc28A8BMMA9+yg==",
            "__VIEWSTATEGENERATOR": "EC4ACD6F",
            "__EVENTVALIDATION": "/wEdAAdtFULLXu4cXg1Ju23kPkBZVobCVrNyCM2j+bEk3ygqmn1KZjrCXCJtWs9HrcHg6Q64ro36uTSn/Z2SUlkm9HsG7WOv0RDD9teZWjlyl84iRMtpPncyBi1FXkZsaSW6dwqO1N1XNFmfsMXJasjxX85jz8PxJxwgNJLTNVe2Bh/bcg5jDf8=",
            "today": date.today().strftime("%Y%m%d"),
            "sortBy": "stockcode",
            "sortDirection": "asc",
            "alertMsg": "",
            "txtShareholdingDate": self.currentDate.strftime("%Y/%m/%d"),
            "btnSearch": ""
        }
        yield FormRequest(url=url,
                          callback=self.parse,
                          formdata=form)

    def send_next_request(self):
        logging.info("trigger next date, current %s, end: %s", self.currentDate, self.endDate)
        if self.currentDate < self.endDate:
            self.currentDate = self.currentDate + timedelta(days=1)
            logging.info("trigger next date inside, current %s, end: %s", self.currentDate, self.endDate)
            url = 'https://www.hkexnews.hk/sdw/search/mutualmarket_c.aspx?t=sh&t=sh'
            form = {
                "__VIEWSTATE": "/wEPDwUJNjIxMTYzMDAwZGQ79IjpLOM+JXdffc28A8BMMA9+yg==",
                "__VIEWSTATEGENERATOR": "EC4ACD6F",
                "__EVENTVALIDATION": "/wEdAAdtFULLXu4cXg1Ju23kPkBZVobCVrNyCM2j+bEk3ygqmn1KZjrCXCJtWs9HrcHg6Q64ro36uTSn/Z2SUlkm9HsG7WOv0RDD9teZWjlyl84iRMtpPncyBi1FXkZsaSW6dwqO1N1XNFmfsMXJasjxX85jz8PxJxwgNJLTNVe2Bh/bcg5jDf8=",
                "today": date.today().strftime("%Y%m%d"),
                "sortBy": "stockcode",
                "sortDirection": "asc",
                "alertMsg": "",
                "txtShareholdingDate": self.currentDate.strftime("%Y/%m/%d"),
                "btnSearch": ""
            }
            yield FormRequest(url=url,
                              callback=self.parse,
                              formdata=form)

    def parse(self, response):
        date_expression = '//div[@id="pnlResult"]/h2[@class="ccass-heading"]/span/text()'
        # date field in html is like "持股日期: 2020/06/19", extract the formal date field
        date_str = response.xpath(date_expression).extract()[0].split()[-1]
        if date_str in self.dateSet:
            # send next date
            #self.send_next_request()
            if self.currentDate < self.endDate:
                self.currentDate = self.currentDate + timedelta(days=1)
                logging.info("trigger next date inside, current %s, end: %s", self.currentDate, self.endDate)
                url = 'https://www.hkexnews.hk/sdw/search/mutualmarket_c.aspx?t=sh&t=sh'
                form = {
                    "__VIEWSTATE": "/wEPDwUJNjIxMTYzMDAwZGQ79IjpLOM+JXdffc28A8BMMA9+yg==",
                    "__VIEWSTATEGENERATOR": "EC4ACD6F",
                    "__EVENTVALIDATION": "/wEdAAdtFULLXu4cXg1Ju23kPkBZVobCVrNyCM2j+bEk3ygqmn1KZjrCXCJtWs9HrcHg6Q64ro36uTSn/Z2SUlkm9HsG7WOv0RDD9teZWjlyl84iRMtpPncyBi1FXkZsaSW6dwqO1N1XNFmfsMXJasjxX85jz8PxJxwgNJLTNVe2Bh/bcg5jDf8=",
                    "today": date.today().strftime("%Y%m%d"),
                    "sortBy": "stockcode",
                    "sortDirection": "asc",
                    "alertMsg": "",
                    "txtShareholdingDate": self.currentDate.strftime("%Y/%m/%d"),
                    "btnSearch": ""
                }
                yield FormRequest(url=url,
                                  callback=self.parse,
                                  formdata=form)
        else:
            self.dateSet.add(date_str)
            stock_table = response.xpath('//table[@id="mutualmarket-result"]/tbody/tr[not(contains(@class,"thread"))]')
            for line in stock_table:
                item = HKBuyStock()
                code_expression = 'td[@class="col-stock-code"]/div[@class="mobile-list-body"]/text()'
                item['code'] = line.xpath(code_expression).extract()[0]
                name_expression = 'td[@class="col-stock-name"]/div[@class="mobile-list-body"]/text()'
                item['name'] = line.xpath(name_expression).extract()[0]
                shareholding_expression = 'td[@class="col-shareholding"]/div[@class="mobile-list-body"]/text()'
                # shareholding format is like "1,111,111,111"
                shareholding_str = line.xpath(shareholding_expression).extract()[0]
                item['shareholding'] = int(''.join(shareholding_str.split(',')))
                shareholding_percent_expression = \
                    'td[@class="col-shareholding-percent"]/div[@class="mobile-list-body"]/text()'
                # shareholding_percent format is like "1.25%"
                shareholding_percent_str = line.xpath(shareholding_percent_expression).extract()[0]
                item['shareholding_percent'] = float(shareholding_percent_str.split("%")[0]) / 100
                item['date'] = date_str
                item['uuid'] = str(uuid.uuid4())
                logging.info("get one stock: %s, %s, %s, %s",
                             item['code'], item['name'], item['shareholding'], item['shareholding_percent'])
                yield item
            # yield next request
            #self.send_next_request()
            logging.info("trigger next date, current %s, end: %s", self.currentDate, self.endDate)
            if self.currentDate < self.endDate:
                self.currentDate = self.currentDate + timedelta(days=1)
                logging.info("trigger next date inside, current %s, end: %s", self.currentDate, self.endDate)
                url = 'https://www.hkexnews.hk/sdw/search/mutualmarket_c.aspx?t=sh&t=sh'
                form = {
                    "__VIEWSTATE": "/wEPDwUJNjIxMTYzMDAwZGQ79IjpLOM+JXdffc28A8BMMA9+yg==",
                    "__VIEWSTATEGENERATOR": "EC4ACD6F",
                    "__EVENTVALIDATION": "/wEdAAdtFULLXu4cXg1Ju23kPkBZVobCVrNyCM2j+bEk3ygqmn1KZjrCXCJtWs9HrcHg6Q64ro36uTSn/Z2SUlkm9HsG7WOv0RDD9teZWjlyl84iRMtpPncyBi1FXkZsaSW6dwqO1N1XNFmfsMXJasjxX85jz8PxJxwgNJLTNVe2Bh/bcg5jDf8=",
                    "today": date.today().strftime("%Y%m%d"),
                    "sortBy": "stockcode",
                    "sortDirection": "asc",
                    "alertMsg": "",
                    "txtShareholdingDate": self.currentDate.strftime("%Y/%m/%d"),
                    "btnSearch": ""
                }
                yield FormRequest(url=url,
                                  callback=self.parse,
                                  formdata=form)