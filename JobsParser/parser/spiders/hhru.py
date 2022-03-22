import scrapy
from parser.items import JobparserItem


class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?area=1&search_field=name&search_field=company_name&search_field=description&text=python',
                  'https://hh.ru/search/vacancy?area=2&search_field=name&search_field=company_name&search_field=description&text=python']

    def parse(self, response):
        next_page = response.xpath('//a[@data-qa="pager-next"]/@href').get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath('//a[@data-qa="vacancy-serp__vacancy-title"]/@href').getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response):
        name_val = response.xpath('//h1/text()').get()
        salary_val = response.xpath('//div[@data-qa="vacancy-salary"]//text()').getall()
        url_val = response.url
        yield JobparserItem(name=name_val, salary=salary_val, url=url_val, _id=url_val)
