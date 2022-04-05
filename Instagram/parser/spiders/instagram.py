import scrapy
from parser.items import ParserItem
from scrapy.loader import ItemLoader
import json
from urllib.parse import urlencode
from copy import deepcopy

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com', 'i.instagram.com']
    start_urls = ['https://www.instagram.com/']
    login_url = 'https://www.instagram.com/accounts/login/ajax/'
    form_data = {
        'enc_password': '#PWD_INSTAGRAM_BROWSER:10:1649179683:AeRQABDMA5g4NNVW2jv9TvelAnBh6UNGJxDuSg1+KCT/lgU1NwO4P5NTnjIQSsvudlfjQeSugnULtzDvNbYaH07PdXcjhVuzGPEeMfyO1Ls46MxOLS/xex3qVseSts16AQdHUbjuhnJ/LJnxdmEsHQ80fA==',
        'username': 'sergeyinsta@s1temaker.ru'
    }
    users_parse = ['boy.squin', 'mustafa.askhek', 'bang.bang4045']
    headers = {'User-Agent': 'Instagram 155.0.0.37.107'}

    def parse(self, response):
        csrf = json.loads(response.xpath('//script[contains(text(), "window._sharedData = ")]/text()').get().replace('window._sharedData = ', '').rstrip(';')).get('config').get('csrf_token')
        yield scrapy.FormRequest(
            self.login_url,
            method='POST',
            callback=self.login,
            formdata=self.form_data,
            headers={'x-csrftoken': csrf}
        )

    def login(self, response):
        j_data = response.json();
        if j_data['authenticated']:
            for user in self.users_parse:
                yield response.follow(
                    f'/{user}',
                    callback=self.user_data_parse,
                    cb_kwargs={'username': user}
                )

    def user_data_parse(self, response, username):
        j_data = json.loads(response.xpath('//script[contains(text(), "window._sharedData = ")]/text()').get().replace('window._sharedData = ', '').rstrip(';'))
        usr_id = j_data.get('entry_data').get('ProfilePage')[0].get('graphql').get('user').get('id')
        params = {'count': 12}
        if j_data.get('entry_data').get('ProfilePage')[0].get('graphql').get('user').get('edge_follow').get('count') > 0:
            url = f'https://i.instagram.com/api/v1/friendships/{usr_id}/following/?{urlencode(params)}';
            yield response.follow(
                url,
                callback=self.follow_data_parse,
                cb_kwargs={
                    'collection': 'following',
                    'username': username,
                    'usr_id': usr_id,
                    'params': deepcopy(params)
                },
                headers=self.headers
            )
        if j_data.get('entry_data').get('ProfilePage')[0].get('graphql').get('user').get('edge_followed_by').get('count') > 0:
            params['search_surface'] = 'follow_list_page'
            url = f'https://i.instagram.com/api/v1/friendships/{usr_id}/followers/?{urlencode(params)}';
            yield response.follow(
                url,
                callback=self.follow_data_parse,
                cb_kwargs={
                    'collection': 'followers',
                    'username': username,
                    'usr_id': usr_id,
                    'params': deepcopy(params)
                },
                headers=self.headers
            )

    def follow_data_parse(self, response, collection, username, usr_id, params):
        j_data = response.json()
        if j_data.get('big_list'):
            params['max_id'] = j_data.get('next_max_id')
            url = f'https://i.instagram.com/api/v1/friendships/{usr_id}/{collection}/?{urlencode(params)}';
            yield response.follow(
                url,
                callback=self.follow_data_parse,
                cb_kwargs={
                    'collection': collection,
                    'username': username,
                    'usr_id': usr_id,
                    'params': deepcopy(params)
                },
                headers=self.headers
            )
        data = j_data.get('users')
        for dt in data:
            item = ParserItem(
                _id=f'{usr_id}_{dt.get("pk")}',
                collection=collection,
                username=username,
                usr_id=usr_id,
                data=dt
            )
            yield item
