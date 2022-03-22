import scrapy
from parser.items import BookparserItem


class LabirintruSpider(scrapy.Spider):
    name = 'labirintru'
    allowed_domains = ['labirint.ru']
    start_urls = ['https://www.labirint.ru/search/java%20script/']

    def parse(self, response):
        next_page = response.xpath('//div[@class="pagination-next"]/a[@class="pagination-next__text"]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath('//a[contains(@class,"buy-link")]//ancestor::div[contains(@class,"card-column")]\
                                //a[@class="cover"]/@href').getall()
        for link in links:
            yield response.follow(link, callback=self.book_parse)

    def book_parse(self, response):
        url_val = response.url
        name_val = response.xpath('//h1/text()').get()
        authors_val = response.xpath('//a[@data-event-label="author"]/text()').get()
        price_val = response.xpath('//span[@class="buying-pricenew-val-number"]/text()').get()
        if response.xpath('//span[@class="buying-priceold-val-number"]'):
            old_price_val = response.xpath('//span[@class="buying-priceold-val-number"]/text()').get()
        else:
            old_price_val = 0
        rating_val = response.xpath('//div[@id="rate"]/text()').get()
        yield BookparserItem(_id=url_val, url=url_val, name=name_val, authors=authors_val, price=price_val,
                             old_price=old_price_val, rating=rating_val)
