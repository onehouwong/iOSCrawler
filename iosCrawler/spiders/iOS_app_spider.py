import scrapy
import base64
import time
import requests
import simplejson
from iosCrawler.items import iOSappItem


class iOS_app_spider(scrapy.Spider):
    name = 'ios'
    allowed_domain = ['25pp.com']   # crawl apps from 25pp
    base_url_soft = '-'
    base_url_game = 'http://ppmac2.25pp.com/jb_app_v2/index.html#u_game_%d_1_5_%d'
    detail_url = 'https://www.25pp.com/ios/detail_%s'
    start_urls = []

    def __init__(self):
        scrapy.Spider.__init__(self)
        '''
        INDEX_APP = range(88, 107)    # category index of normal apps
        INDEX_APP.append(167)
        INDEX_GAME = range(72, 85)  # category index of game apps
        INDEX_GAME.append(169)
        # initialize urls of each category
        for index in INDEX_APP:
            self.start_urls.append(self.base_url_soft % (index, 1))

        for index in INDEX_GAME:
            self.start_urls.append(self.base_url_game % (index, 1))
        '''
        # for testing
        self.start_urls.append(self.base_url_soft % (88, 1))

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url, dont_filter=True)

    @staticmethod
    def post_request_for_app(category, page):
        url = "http://jsondata.25pp.com/index.html"

        headers = {
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
            'Accept': "*/*",
            'Referer': "http://jsondata.25pp.com/index.html?tunnel-command=4261421120",
            'Content-Type': "application/x-www-form-urlencoded",
            'Accept-Language': "zh-cn",
            'Tunnel-Command': "4261421088",
            'Accept-Encoding': "gzip, deflate",
            'Host': "jsondata.25pp.com",
            'Cache-Control': "no-cache",
            'Postman-Token': "7258984e-99b9-4e41-8920-53a5c19d5d19"
        }

        # parameters
        # dcType:   device type.    0.all,      1.iphone,   2.ipad
        # resType:  resource type.  1.software  2.games
        # listType: list type       1.newest    2.hottest   3.week top  4.month top 5.top board
        # catId:    category type   [88, 106]+167 for soft      [72,84]+169 for game    all for jail-broken apps
        # perCount: number of apps in one page
        # page:     page number
        payload = '{"dcType":0,"resType":1,"listType":5,"catId":%d,"perCount":32,"page":%d}' % (category, page)
        response = requests.request("POST", url, data=payload, headers=headers)
        return response

    # For each category
    # find out the max pages and yield requests of each page
    def parse(self, response):
        selector = scrapy.Selector(response)
        counts = selector.xpath('//div[@id="js-app-page"]/a[@class="page-number"]/text()').extract()
        max_page_count = int(counts[-2])
        # print response.url + "    " + str(max_page_count)

        for count in range(max_page_count):
            url = response.url[:-1] + str(count+1)
            yield scrapy.Request(url, callback=self.parse_page)

    # For each page
    # parse each page
    def parse_page(self, response):
        selector = scrapy.Selector(response)
        appids = selector.xpath('//ul[@id="js-app-list"]/li/a/@data-appid').extract()
        print appids
        print appids.__len__()

        for i in appids:
            url = self.detail_url % i
            yield scrapy.Request(url, callback=self.parse_detail_page)
            time.sleep(0.2)

    # For each app
    # parse each detail page of an app
    def parse_detail_page(self, response):
        selector = scrapy.Selector(response)
        item = iOSappItem()
        # start parsing details
        try:
            item.set_attr('title', selector.xpath('//h2[@class="app-title ellipsis"]/@title').extract()[0])
        except IndexError:
            item.set_attr('title', '')

        try:
            item.set_attr('category', selector.xpath('//div[@class="crumb"]/a/text()').extract()[-1])
        except IndexError:
            item.set_attr('category', '')

        try:
            item.set_attr('update', selector.xpath('//span[@class="col-1 ellipsis"]/strong/text()').extract()[0])
        except IndexError:
            item.set_attr('update', '')

        try:
            item.set_attr('version', selector.xpath('//span[@class="col-1 ellipsis"]/strong/text()').extract()[1])
        except IndexError:
            item.set_attr('version', '')

        try:
            item.set_attr('source', response.url)
        except IndexError:
            item.set_attr('source', '')

        try:
            item.set_attr('size', selector.xpath('//span[@class="col-2 ellipsis"]/strong/text()').extract()[0])
        except IndexError:
            item.set_attr('size', '')

        try:
            item.set_attr('req', selector.xpath('//span[@class="col-2 ellipsis"]/strong/text()').extract()[1])
        except IndexError:
            item.set_attr('req', '')

        try:
            item.set_attr('des', selector.xpath('//div[@class="app-desc ellipsis"]/text()').extract()[0])
        except IndexError:
            item.set_attr('des', '')

        try:
            item.set_attr('url', base64.b64decode(selector.xpath('//a[@class="btn-install-x"]/@appdownurl').extract()[0]))
        except IndexError:
            item.set_attr('url', '')

        yield item

