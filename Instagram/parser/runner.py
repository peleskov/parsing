from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from parser import settings
from parser.spiders.instagram import InstagramSpider


if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    # query = input('')
    process.crawl(InstagramSpider, search='обои')

    process.start()
