# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import Join, MapCompose, Compose, TakeFirst


def get_price(value):
    value = value[0].replace(' ', '')
    try:
        return float(value)
    except:
        return value


def get_chars(chars):
    chars = [c.strip() for c in chars]
    return [(chars[i], chars[i + 1]) for i in range(0, len(chars)-1, 2)]


class ParserItem(scrapy.Item):
    _id = scrapy.Field(output_processor=TakeFirst())
    url = scrapy.Field(output_processor=TakeFirst())
    name = scrapy.Field(output_processor=Join())
    price = scrapy.Field(input_processor=Compose(get_price), output_processor=TakeFirst())
    photos = scrapy.Field()
    characteristics = scrapy.Field(input_processor=Compose(get_chars), output_processor=Compose())
