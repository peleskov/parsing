import scrapy
from parser.items import ParserItem
from scrapy.loader import ItemLoader


class CastoramaSpider(scrapy.Spider):
    name = 'castorama'
    allowed_domains = ['www.castorama.ru']
    start_urls = ['https://www.castorama.ru/decoration/wallpaper/paintable-wallpaper',
                  'https://www.castorama.ru/lighting/interior-lighting/lighting-accessories']

    def parse(self, response):
        next_page = response.xpath('//div[contains(@class,"toolbar-bottom")]//a[@class="next i-next"]')
        if next_page:
            yield response.follow(next_page[0], callback=self.parse)
        links = response.xpath('//a[contains(@class, "product-card__name")]')
        for link in links:
            yield response.follow(link, callback=self.parse_goods)

    def parse_goods(self, response):
        loader = ItemLoader(item=ParserItem(), response=response)
        loader.add_value("_id", response.url)
        loader.add_value("url", response.url)
        loader.add_xpath("name", '//h1/text()')
        loader.add_xpath("price", '(//span[@class="price"])[1]/span/span[not(@class="currency")]/text()')
        loader.add_xpath("photos", '//img[contains(@class, "top-slide__img")]/@data-src')
        loader.add_xpath("characteristics", '//dl//*[contains(@class, "specs-table__attribute-name")]/text() | //*[contains(@class, "specs-table__attribute-value")]/text()')
        yield loader.load_item()
