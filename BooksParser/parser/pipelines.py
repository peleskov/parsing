# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class BookparserPipeline:
    def __init__(self):
        client = MongoClient('192.168.1.200', 27017)
        self.books_db = client.books

    def process_item(self, item, spider):
        item['price'] = float(str(item['price']).replace(' ₽ ', '').strip())
        item['old_price'] = float(str(item['old_price']).replace(' ₽ ', '').replace('\xa0', '').strip())
        item['rating'] = float(item['rating'].replace(',', '.'))
        item['name'] = item['name'].strip()
        item['authors'] = item['authors'].strip()
        collection = self.books_db[spider.name]
        if not collection.find_one({'_id': item['_id']}):
            collection.insert_one(item)
        return item
