from scrapy import cmdline
cmdline.execute('scrapy crawl northCapital -a startDate=2020-06-30 -a duration=7'.split())