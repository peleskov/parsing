from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from parser import settings
from parser.spiders.hhru import HhruSpider
from parser.spiders.superjobru import SuperjobruSpider

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(HhruSpider)
    crawler_process.crawl(SuperjobruSpider)
    crawler_process.start()
