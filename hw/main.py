import requests
from lxml import html
import hashlib
from pymongo import MongoClient
from pprint import pprint
from datetime import datetime


HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
    'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,ro;q=0.6'
}
client = MongoClient('192.168.1.200', 27017)
db = client['news']
NEWS_DB = db.news
# NEWS_DB.drop()


def get_news(url):
    id_hash = hashlib.md5(url.encode())
    # Поиск именно по _id = hash от URL новости,
    # потому что URL новости, уникален, а ID новости на разных сайтах может повториться
    # и hash зачастую короче чем URL
    if not NEWS_DB.find_one({'_id': id_hash.hexdigest()}):
        res = requests.get(url, headers=HEADERS)
        if res.ok:
            return res.text
        else:
            print(url, ' - Bed request!')
            return False
    else:
        return False


def mail_ru(main_url):
    res = get_news(main_url)
    if res:
        dom = html.fromstring(res)
        urls = dom.xpath('//div[contains(@class, "daynews__item")]/a/@href')
        urls.extend(dom.xpath('//li[@class="list__item"]/a[@class="list__text"]/@href'))
        for url in urls:
            res_text = get_news(url)
            if res_text:
                dom = html.fromstring(res_text)
                id_hash = hashlib.md5(url.encode())
                news = {
                    '_id': id_hash.hexdigest(),
                    'donor': main_url,
                    'url': url,
                    'date': datetime.strptime(dom.xpath('//span[@datetime]/@datetime')[0], '%Y-%m-%dT%H:%M:%S%z'),
                    'source': {
                        'name': dom.xpath('//a[contains(@class, "breadcrumbs__link")]/span/text()')[0],
                        'url': dom.xpath('//a[contains(@class, "breadcrumbs__link")]/@href')[0]
                    },
                    'title': dom.xpath('//h1[@class="hdr__inner"]/text()')[0]
                }
                NEWS_DB.insert_one(news)


def yandex_ru(main_url):
    HEADERS['cookie'] = 'yandexuid=8862211521645804464; yuidss=8862211521645804464; mda=0; is_gdpr=1; is_gdpr_b=CJv7eBC0ZBgBKAE=; my=YwA=; gdpr=0; _ym_uid=1645867617708331657; ymex=1677403617.yrts.1645867617; yandex_gid=10487; Session_id=3:1646023878.5.0.1646023878012:a8dgTg:58.1.2:1|6038582.0.2|3:248735.5292.woI6spf-EimqSmyVymG7_UZJQhg; sessionid2=3:1646023878.5.0.1646023878012:a8dgTg:58.1.2:1|6038582.0.2|3:248735.5292.woI6spf-EimqSmyVymG7_UZJQhg; L=VwRaX3xfW3wGW2VEdQNtSld9XGwAeUl/IlU6VgIZXzo=.1646023878.14902.345238.b408eaefee5017eb506cbedca5bbe8e6; yandex_login=peleskov; yabs-sid=119496901646069285; i=cF3EujYI3ZS305gy3EZ+jF69TLkobG//9WiKci9+tXt3hY4dgnMSIxMKt6vN6ptxMgao2oVXJTqkGqEHGNQ44VfWPqs=; _ym_d=1646110081; _ym_isad=2; yabs-frequency=/5/0000000000000000/7Q0_ROO0001eHK62OK5jXW0006X58m00/; yp=1648788491.csc.1#1648466442.ygu.1#1648466444.spcs.l#1646479247.mcv.0#1646479247.mct.null#1661878082.szm.1:1920x1200:1920x503#1961383878.udn.cDpwZWxlc2tvdg==#1646634325.mcl.q5tdy0#1646146629.nwcst.1646066400_10487_1; _yasc=VlwiS2QumQmID7bRu6CIOdfc+XrX5l+8parRQ+2WdohM0RPNAycRraCIeSA=; cycada=MNS7Flrh7L1o5WO1gVaZ2S8LvBuerP3AYRV+5P+3ClM='
    res = get_news(main_url)
    if res:
        dom = html.fromstring(res)
        news_list = dom.xpath('//section[@aria-labelledby="top-heading"]//div[contains(@class, "mg-grid__col")]')
        for news_block in news_list:
            url = news_block.xpath('.//a[@class="mg-card__link"]/@href')[0]
            res_orig = get_news(url)
            source_url = ''
            if res_orig:
                dom_orig = html.fromstring(res_orig)
                source_url = dom_orig.xpath('//a[@class="mg-story__title-link"]/@href')[0]
            id_hash = hashlib.md5(url.encode())
            news_time = news_block.xpath('.//span[@class="mg-card-source__time"]/text()')[0]
            news = {
                '_id': id_hash.hexdigest(),
                'donor': main_url,
                'url': url,
                'date': datetime.strptime(datetime.now().strftime(f'%Y-%m-%dT{news_time}:00'), '%Y-%m-%dT%H:%M:%S'),
                'source': {
                    'name': news_block.xpath('.//a[@class="mg-card__source-link"]/text()')[0],
                    'url': source_url
                },
                'title': news_block.xpath('.//a[@class="mg-card__link"]/text()')[0]
            }
            NEWS_DB.insert_one(news)


if __name__ == '__main__':
    mail_ru('https://news.mail.ru/')
    yandex_ru('https://yandex.ru/news/')
    # lenta_ru('https://lenta.ru/') Сегодня не доступен сайт!!!

    pprint(len(list(NEWS_DB.find({}))))
    pprint(list(NEWS_DB.find({})))
