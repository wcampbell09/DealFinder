# -*- coding: utf-8 -*-
import scrapy


class ProductsSpider(scrapy.Spider):
    name = 'products'
    allowed_domains = ['gainesville.craigslist.org']
    start_urls = ['http://gainesville.craigslist.org/d/for-sale/search/sss/']

    def parse(self, response):
        # listings = response.xpath('//a[@class="result-title hdrlnk"]/text()').extract()
        # for listing in listings:
        #     yield {
        #         'Listing': listing,
        #     }
        listings = response.xpath('//li[@class="result-row"]')
        for listing in listings:
            date = listing.xpath('.//*[@class="result-date"]/@datetime').extract_first()
            link = listing.xpath('.//a[@class="result-title hdrlnk"]/@href').extract_first()
            text = listing.xpath('.//a[@class="result-title hdrlnk"]/text()').extract_first()
            # price = listing.xpath('.//*[@class="result-price"]/text()').extract_first()

            yield scrapy.Request(link,
                                callback=self.parse_listing,
                                meta={'date': date,
                                    'link': link,
                                    'text': text
                                    # 'price': price
                                    })
        
        next_page_url = response.xpath('//a[text()="next > "]/@href').extract_first()
        if next_page_url:
            yield scrapy.Request(response.urljoin(next_page_url), callback=self.parse)

    def parse_listing(self, response):
        date = response.meta['date']
        link = response.meta['link']
        text = response.meta['text']
        # price = response.meta['price']