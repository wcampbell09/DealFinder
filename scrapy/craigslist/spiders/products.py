# -*- coding: utf-8 -*-
import scrapy
import os
import csv
import glob
import psycopg2

class ProductsSpider(scrapy.Spider):
    name = 'products'
    allowed_domains = ['gainesville.craigslist.org']
    start_urls = ['http://gainesville.craigslist.org/d/for-sale/search/sss/']

    def parse(self, response):
        listings = response.xpath('//li[@class="result-row"]')
        for listing in listings:
            date = listing.xpath('.//*[@class="result-date"]/@datetime').extract_first()
            link = listing.xpath('.//a[@class="result-title hdrlnk"]/@href').extract_first()
            title = listing.xpath('.//a[@class="result-title hdrlnk"]/text()').extract_first()
            price = listing.xpath('.//*[@class="result-price"]/text()').extract_first()

            yield scrapy.Request(link,
                                callback=self.parse_listing,
                                meta={'date': date,
                                    'link': link,
                                    'title': title,
                                    'price': price
                                    })
        
        next_page_url = response.xpath('//a[text()="next > "]/@href').extract_first()
        if next_page_url:
            yield scrapy.Request(response.urljoin(next_page_url), callback=self.parse)

    def parse_listing(self, response):
        date = response.meta['date']
        link = response.meta['link']
        title = response.meta['title']
        price = response.meta['price']
        
        place = response.xpath('//small/text()').extract_first()

        images = response.xpath('//*[@id="thumbs"]//@src').extract()
        images = [image.replace('50x50c', '600x450') for image in images]
         
        description = response.xpath('//*[@id="postingbody"]/text()').extract()

        yield {
            'date': date,
            'link': link,
            'title': title,
            'price': price,
            'images': images,
            'description': description,
            'place': place
        }
        def close( self, reason):
            csv_file = max(glob.iglog('*.csv'), key=os.path.getctime)

            conn = psycopg2.connect(host="localhost", database="deeple", user="wesley", password="postgres")
            cursor = conn.cursor()
            csv_data = csv.reader(file(csv_file))

            row_count = 0
            for row in csv_data:
                if row_count != 0:
                    cursor.execute('INSERT IGNORE INTO deeple_table(date, link, title, price, images, description, place) VALUES(%s, %s, %s, %s, %s, %s, %s)', row)
                row_count += 1

            conn.commit()
            cursor.close()