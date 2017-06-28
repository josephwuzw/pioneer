# -*- coding: utf-8 -*-
import re

import demjson
import scrapy
from scrapy.http import Request
from pyquery import PyQuery

from pioneer.settings import COOKIES_PIONEER_JSON

cookies = demjson.decode(COOKIES_PIONEER_JSON)

class IntelligynceSpider(scrapy.Spider):

    name = 'intelligynce'
    allowed_domains = ['intelligynce.com']
    start_urls = [
            'https://intelligynce.com/Members/_ProductsTablePartial?productsPage=1&X-Requested-With=XMLHttpRequest%2CXMLHttpRequest%2CXMLHttpRequest&X-Requested-With=XMLHttpRequest'
            ]

    def make_requests_from_url(self, url):
        return Request(url, self.parse_page, dont_filter=True, cookies=cookies)

    def parse_page(self, response):
        pq = PyQuery(response.body)
        trs = pq('#productSearchResultsContainer > table > tbody > tr')
        gen = trs.items()
        for each in gen:
            url = each('td > div > a:nth-child(3)').attr['href']
            _discard = gen.next()
            td_attrs = gen.next()
            attrs = [td.text().replace(' ', '').replace('\r\n', ' ') for td in td_attrs('td').items()]

            yield {
                    'url':url,
                    'attrs':attrs,
                    }

        page = re.findall('productsPage=(\d+)', response.url)
        assert len(page) == 1
        page = int(page[0])

        nexturl = re.sub('productsPage={}'.format(page), 'productsPage={}'.format(page+1), response.url)
        yield Request(nexturl, self.parse_page)
