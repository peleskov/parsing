import scrapy
from parser.items import BookparserItem
from urllib.parse import urlparse


class Book24ruSpider(scrapy.Spider):
    name = 'book24ru'
    allowed_domains = ['book24.ru']
    start_urls = ['https://book24.ru/search?q=java']

    def parse(self, response):
        url = urlparse(response.url)
        folders = [i for i in url.path.split('/') if i]
        if len(folders) > 1:
            page = folders[1].split('-')
            folders[1] = f'{page[0]}-{int(page[1]) + 1}'
        else:
            folders.append('page-2')
        next_page = url._replace(path='/'.join(folders)).geturl()
        if response.status == 200:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath('//*[contains(text(),"В корзину")]//ancestor::div[@class="product-card__content"]\
                                /a/@href').getall()
        for link in links:
            yield response.follow(link, callback=self.book_parse)

    def book_parse(self, response):
        url_val = response.url
        name_val = response.xpath('//h1/text()').get()
        authors_val = response.xpath('(//ul[@class="product-characteristic__list"])[1]/li[1]\
                                        //*[@class="product-characteristic__value"]//text()').get()
        price_val = response.xpath('//meta[@itemprop="price"]/@content').get()
        if response.xpath('//span[contains(@class, "product-sidebar-price__price-old")]'):
            old_price_val = response.xpath('//span[contains(@class, "product-sidebar-price__price-old")]//text()').get()
        else:
            old_price_val = 0
        rating_val = response.xpath('//div[@itemprop="aggregateRating"]/meta[@itemprop="ratingValue"]/@content').get()
        yield BookparserItem(_id=url_val, url=url_val, name=name_val, authors=authors_val, price=price_val,
                             old_price=old_price_val, rating=rating_val)
