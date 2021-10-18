import requests
from lxml import html
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as dke
from pprint import pprint
import pandas as pd


def XPath():
    """
    Написать приложение, которое собирает основные новости с сайта на выбор news.mail.ru, lenta.ru, yandex-новости.
    Для парсинга использовать XPath. Структура данных должна содержать:
        название источника;
        наименование новости;
        ссылку на новость;
        дата публикации.
    Сложить собранные новости в БД
    """
    d_news = {
        'source': [],
        'title': [],
        'ref': [],
        'date': []
    }

    url = 'https://yandex.ru/news/?utm_source=main_stripe_big'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'}
    response = requests.get(url, headers=headers)

    dom = html.fromstring(response.text)

    articles = dom.xpath('//article')

    for rec in articles:
        source = rec.xpath('.//a[@class="mg-card__source-link"]/text()')[0]
        title = rec.xpath('.//h2/text()')[0].replace('\xa0', ' ')
        ref = rec.xpath('.//a/@href')[0]
        date = rec.xpath('.//span[@class="mg-card-source__time"]/text()')[0]

        d_news['source'].append(source)
        d_news['title'].append(title)
        d_news['ref'].append(ref)
        d_news['date'].append(date)
    return pd.DataFrame.from_dict(d_news)


def ex():
    df_news = XPath()

    client = MongoClient('127.0.0.1', 27017)
    db = client['News_1018']
    news_land = db.news_land

    data_dict = df_news.to_dict("records")
    for rec in data_dict:
        try:
            news_land.insert_one(rec)
        except dke:
            print("Already exist")


ex()
