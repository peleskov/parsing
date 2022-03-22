# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class BookparserItem(scrapy.Item):
    _id = scrapy.Field()
    url = scrapy.Field()
    name = scrapy.Field()
    authors = scrapy.Field()
    price = scrapy.Field()
    old_price = scrapy.Field()
    rating = scrapy.Field()
