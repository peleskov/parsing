from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common import exceptions
from selenium.webdriver.chrome.options import Options
from pymongo import MongoClient
import hashlib
from pprint import pprint
import time

client = MongoClient('192.168.1.200', 27017)
db = client['mails']
MAILS_DB = db.mails
# MAILS_DB.drop()


def get_mails():
    auth = {
        'url': 'https://account.mail.ru/login',
        'login': 'study.ai_172@mail.ru',
        'password': 'NextPassword172#'
    }
    service = ChromeService(executable_path="./chromedriver.exe")
    '''Скроем окно браузера'''
    options = Options()
    options.add_argument('headless')
    with webdriver.Chrome(service=service, options=options) as driver:
        # driver = webdriver.Chrome(service=service)
        driver.maximize_window()
        driver.get(auth['url'])

        '''Авторизуемся'''
        WebDriverWait(driver, 60).until(lambda d: d.find_element(By.XPATH, '//input[@name="username"]'))
        element = driver.find_element(By.XPATH, '//input[@name="username"]')
        element.send_keys(auth['login'] + Keys.ENTER)
        time.sleep(1)
        element = driver.find_element(By.XPATH, '//input[@name="password"]')
        element.send_keys(auth['password'] + Keys.ENTER)

        '''Получаем ссылки на письма'''
        WebDriverWait(driver, 60).until(lambda d: d.find_element(By.XPATH, '//div[contains(@class, "scrollable_content")]'))
        try:
            '''Примем cookie если есть popup с кнопкой'''
            driver.find_element(By.XPATH, '//span[@id="cmpwelcomebtnyes"]/a').click()
        except exceptions.NoSuchElementException:
            pass
        scroll = driver.find_element(By.XPATH, '//div[contains(@class, "scrollable_content")]')
        url_list = set()
        while True:
            time.sleep(0.5)
            try:
                links = scroll.find_elements(By.XPATH, '//a[@data-uidl-id]')
                for link in links:
                    url_list.add(link.get_attribute('href'))
            except exceptions.ElementNotInteractableException as ex:
                print(ex)
            try:
                driver.find_element(By.XPATH, '//a[contains(@class, "_last")]')
                break
            except exceptions.NoSuchElementException:
                pass
            scroll.send_keys(Keys.PAGE_DOWN)

        '''Пройдем по все письмам и соберем информацию'''
        for url in url_list:
            id_hash = hashlib.md5(url.encode())
            if not MAILS_DB.find_one({'_id': id_hash.hexdigest()}):
                driver.get(url)
                WebDriverWait(driver, 60).until(lambda d: d.find_element(By.XPATH, '//div[@class="letter-body"]'))
                body = driver.find_element(By.XPATH, '//div[@class="letter-body"]')
                author = driver.find_element(By.XPATH, '//div[@class="letter__author"]/span')
                date = driver.find_element(By.XPATH, '//div[@class="letter__date"]')
                mail = {
                    '_id': id_hash.hexdigest(),
                    'date': date.text,
                    'author': author.get_attribute('title'),
                    'subject': driver.find_element(By.XPATH, '//h2').text,
                    'body_text': body.text,
                }
                MAILS_DB.insert_one(mail)


if __name__ == '__main__':
    '''mvideo вставили captcha, сделать не получилось'''
    get_mails()
    pprint(len(list(MAILS_DB.find({}))))
    # pprint(list(MAILS_DB.find({})))
