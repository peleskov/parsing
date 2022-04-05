# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient

class ParserPipeline:
    def process_item(self, item, spider):
        print()
        return item

class MongoPipeline:
    def open_spider(self, spider):
        self.client = MongoClient('192.168.1.200', 27017)
        self.insta_db = self.client.insta

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        collection = self.insta_db[item['collection']]
        if not collection.find_one({'_id': item['_id']}):
            collection.insert_one(ItemAdapter(item).asdict())
        return item
