# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import scrapy
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient
import os
from urllib.parse import urlparse
import hashlib
from scrapy.utils.python import to_bytes

class ParserPipeline:
    def process_item(self, item, spider):
        print()
        return item


class MongoPipeline:
    def open_spider(self, spider):
        self.client = MongoClient('192.168.1.200', 27017)
        self.goods_db = self.client.goods

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        collection = self.goods_db[spider.name]
        if not collection.find_one({'_id': item['_id']}):
            collection.insert_one(ItemAdapter(item).asdict())
        return item


class PhotosPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item['photos']:
            for img in item['photos']:
                try:
                    yield scrapy.Request(img)
                except Exception as e:
                    print(e)

    def item_completed(self, results, item, info):
        item['photos'] = [itm[1] for itm in results if itm[0]]
        return item

    def file_path(self, request, response=None, info=None, *, item=None):
        return os.path.join(os.path.basename(urlparse(item['url']).path), f'{hashlib.sha1(to_bytes(request.url)).hexdigest()}.jpg')

