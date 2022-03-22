import scrapy
from parser.items import JobparserItem


class SuperjobruSpider(scrapy.Spider):
    name = 'superjobru'
    allowed_domains = ['superjob.ru', 'spb.superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=python&geo%5Bt%5D%5B0%5D=4',
                  'https://spb.superjob.ru/vacancy/search/?keywords=python']

    def parse(self, response):
        next_page = response.xpath('//a[@rel="next"][2]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath('//div[contains(@class, "f-test-vacancy-item")]//a[@target="_blank"]/@href').getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response):
        name_val = response.xpath('//h1/text()').get()
        salary_val = response.xpath('//h1/parent::div/span/span[1]//text()').getall()
        url_val = response.url
        yield JobparserItem(name=name_val, salary=salary_val, url=url_val, _id=url_val)
