import requests
from bs4 import BeautifulSoup
import os.path
import hashlib
import json
from pymongo import MongoClient
from pprint import pprint


class FindJobs:
    def __init__(self):
        client = MongoClient('192.168.1.200', 27017)
        db = client['vacancy_db']
        self.vacancy = db.vacancy
        self.duplicate = {}
        if input(f'Обновить базу данных (y/n): ') == 'n':
            return
        sites = [{
            'base_url': 'https://hh.ru/',
            'path': 'search/vacancy',
            'tag_np': 'a',
            'attr_np': {'data-qa': 'pager-next'},
            'params': {
                'area': 1,
                'items_on_page': 20,
                'fromSearchLine': 'true',
                'from': 'suggest_post',
                'page': 0
            }
        },
            {
                'base_url': 'https://www.superjob.ru/',
                'path': 'vacancy/search',
                'tag_np': 'a',
                'attr_np': {'rel': 'next'},
                'params': {
                    'geo[t][0]': 4,
                    'page': 1
                }
            }]
        site_key = ''
        site_indexes = [i for i in range(len(sites))]
        while site_key not in site_indexes:
            for k, s in enumerate(sites):
                print(k, s['base_url'])
            site_key = int(input(f'Введите ключ сайта для поиска вакансий {site_indexes}: '))
        self.text = input('Введите ключевое слово для поиска вакансий: ')
        self.site = sites[site_key]
        if site_key == 0:
            self.site['params']['text'] = self.text
        elif site_key == 1:
            self.site['params']['keywords'] = self.text
        request_hash = hashlib.md5(f"{self.site['base_url']}{''.join([f'{key}{val}' for key, val in self.site['params'].items()])}".encode())
        request_folder = os.path.join(os.path.abspath(os.curdir), 'pages', request_hash.hexdigest())
        print(f"Производим поиск вакансий на сайте: {self.site['base_url']} по ключевому слову: {self.text}")
        if not os.path.exists(request_folder):
            """Делаем запрос на сайт только если нет таких сохраненных страниц"""
            if not self.__get_pages(request_folder):
                print(f'Не возможно получить информацию с сайта {self.site["base_url"]}')
        self.jobs = self.__get_data_hh(request_folder) if site_key == 0 else self.__get_data_sj(request_folder)
        print('Добавлено вакансий: ', len(self.jobs))
        print('Повторяющихся вакансий: ', sum([i for i in self.duplicate.values()]))

    def __get_pages(self, folder):
        os.makedirs(folder)
        headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}
        next_page = True
        while next_page is not None:
            res = requests.get(f"{self.site['base_url']}{self.site['path']}", headers=headers, params=self.site['params'])
            if not res.ok:
                return False
            dom = BeautifulSoup(res.text, 'html.parser')
            next_page = dom.find(self.site['tag_np'], self.site['attr_np'])
            with open(os.path.join(folder, f"index{self.site['params']['page']}.html"), 'w', encoding='utf-8') as f:
                f.write(res.text)
            self.site['params']['page'] += 1
        return True

    def __get_data_hh(self, folder):
        """Получаем данные для hh.ru"""
        jobs_list = []
        for f_name in os.listdir(folder):
            with open(os.path.join(folder, f_name), encoding='utf-8') as file:
                dom = BeautifulSoup(file.read(), 'html.parser')
                vacancy_list = dom.find_all('div', {'class': 'vacancy-serp-item'})
                for vacancy in vacancy_list:
                    link_tag = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})
                    link = link_tag.attrs['href'].split('?')[0]
                    salary = {}
                    salary_tag = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
                    if salary_tag:
                        salary_list = list([i.replace('\u202f', '').replace(' ', '').strip() for i in salary_tag.strings])
                        salary['currency'] = salary_list[len(salary_list) - 1].lower()
                        if salary_list[0] == 'от':
                            salary['min'] = int(salary_list[1])
                        elif salary_list[0] == 'до':
                            salary['max'] = int(salary_list[1])
                        else:
                            min_max = salary_list[0].split('–')
                            salary['min'] = int(min_max[0])
                            salary['max'] = int(min_max[1])
                    else:
                        salary['fix'] = 'По договорённости'
                    id_hash = hashlib.md5(link.encode())
                    cur_job = {
                        '_id': id_hash.hexdigest(),
                        'title': link_tag.getText(),
                        'link': link,
                        'site': self.site['base_url'],
                        'salary': salary
                    }
                    if self.__to_db(cur_job):
                        jobs_list.append(cur_job)
        return jobs_list

    def __get_data_sj(self, folder):
        """Получаем данные для superjob.ru"""
        jobs_list = []
        for f_name in os.listdir(folder):
            with open(os.path.join(folder, f_name), encoding='utf-8') as file:
                dom = BeautifulSoup(file.read(), 'html.parser')
                vacancy_list = dom.find_all('div', {'class': 'f-test-vacancy-item'})
                for vacancy in vacancy_list:
                    link_tag = vacancy.find('a')
                    link = f"{self.site['base_url']}{link_tag.attrs['href']}"
                    salary = {}
                    salary_tag = vacancy.find('span', {'class': 'f-test-text-company-item-salary'})
                    if salary_tag:
                        salary_list = list([i.replace('\xa0', '').replace('руб.', '').strip() for i in salary_tag.strings if i not in ('/', '—', '\xa0', 'руб.', 'месяц')])
                        salary['currency'] = 'руб.'
                        if salary_list[0] == 'от':
                            salary['min'] = int(salary_list[1])
                        elif salary_list[0] == 'до':
                            salary['max'] = int(salary_list[1])
                        elif salary_list[0][0:2] == 'По':
                            salary['fix'] = salary_list[0]
                        elif len(salary_list) == 2:
                            salary['min'] = int(salary_list[0])
                            salary['max'] = int(salary_list[1])
                        else:
                            salary['fix'] = int(salary_list[0])
                    id_hash = hashlib.md5(link.encode())
                    cur_job = {
                        '_id': id_hash.hexdigest(),
                        'title': link_tag.getText(),
                        'link': link,
                        'site': self.site['base_url'],
                        'salary': salary
                    }
                    if self.__to_db(cur_job):
                        jobs_list.append(cur_job)
        return jobs_list

    def __to_db(self, cur_job):
        if not self.vacancy.find_one({'_id': cur_job['_id']}):
            self.vacancy.insert_one(cur_job)
            return True
        else:
            self.duplicate.setdefault(cur_job['link'], 0)
            self.duplicate[cur_job['link']] += 1
            return False

    def filter_vacancy(self, sal, cur):
        min_filter = {'$and': [{'salary.min': {'$exists': True}},
                               {'salary.max': {'$exists': False}},
                               {'salary.min': {'$lte': sal}}]}
        max_filter = {'$and': [{'salary.max': {'$exists': True}},
                               {'salary.min': {'$exists': False}},
                               {'salary.max': {'$gte': sal}}]}
        min_max_filter = {'$and': [{'salary.min': {'$exists': True}},
                                   {'salary.max': {'$exists': True}},
                                   {'salary.min': {'$lte': sal}},
                                   {'salary.max': {'$gte': sal}}]}
        return (list(self.vacancy.find(
            {'$and': [{'$or': [min_filter, max_filter, min_max_filter]}, {'salary.currency': {'$regex': cur.lower()}}]})))


if __name__ == '__main__':
    find_jobs = FindJobs()
    pprint(find_jobs.filter_vacancy(150000, 'руб'))
