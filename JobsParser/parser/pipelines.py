# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient


class ParserPipeline:
    def __init__(self):
        client = MongoClient('192.168.1.200', 27017)
        self.jobs_db = client.jobs

    def process_item(self, item, spider):
        salary_min = 0
        salary_max = 0
        salary_cur = 'руб.'
        if spider.name == 'hhru':
            sal = list(val.replace('\xa0', '').replace(' ', '').strip() for val in item['salary'])
            if sal[0] == 'от':
                salary_min = int(sal[1])
                salary_cur = sal[3]
                if sal[2] == 'до':
                    salary_max = int(sal[3])
                    salary_cur = sal[5]
            elif sal[0] == 'до':
                salary_max = int(sal[1])
                salary_cur = sal[3]
            elif sal[0] == 'з/пнеуказана':
                item['salary'] = sal[0]
        else:
            sal = list(val.replace('\xa0', '').replace('руб.', '').strip() for val in item['salary'] if val and val not in ('\xa0', '—', 'руб.', 'месяц'))
            try:
                if sal[0] == 'от':
                    salary_min = int(sal[1])
                if sal[0] == 'до':
                    salary_max = int(sal[1])
                elif sal[0] == 'По договорённости':
                    item['salary'] = sal[0]
                else:
                    salary_min = int(sal[0])
                    salary_max = int(sal[1])
            except:
                pass
        item['salary_min'] = salary_min
        item['salary_max'] = salary_max
        item['salary_cur'] = salary_cur
        collection = self.jobs_db[spider.name]
        if not collection.find_one({'_id': item['_id']}):
            collection.insert_one(item)
        return item
