# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ParserItem(scrapy.Item):
    _id = scrapy.Field()
    collection = scrapy.Field()
    username = scrapy.Field()
    usr_id = scrapy.Field()
    data = scrapy.Field()
