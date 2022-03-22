from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from parser import settings
from parser.spiders.book24ru import Book24ruSpider
from parser.spiders.labirintru import LabirintruSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    crawler_process = CrawlerProcess(settings=crawler_settings)
    # crawler_process.crawl(Book24ruSpider)
    crawler_process.crawl(LabirintruSpider)

    crawler_process.start()
