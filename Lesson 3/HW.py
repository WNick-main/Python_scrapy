import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup as bs
import pandas as pd
import numpy as np

from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as dke
from pprint import pprint


def from_hh():
    url = 'https://hh.ru/search/vacancy'
    d_vacancy = {
        '_id': [],
        'position': [],
        'href': [],
        'salary_from': [],
        'salary_to': [],
        'salary_currency': [],
        'source': []
    }
    for i in range(3):
        params = {
            'clusters': 'true',
            'ored_clusters': 'true',
            'enable_snippets': 'true',
            'salary': '',
            'st': 'searchVacancy',
            'text': 'Python',
            'page': i
        }
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'}

        response = requests.get(url, params=params, headers=headers)

        if response.ok:
            soup = bs(response.text, 'html.parser')
            vacancy_list = soup.find_all('div', attrs={'class': 'vacancy-serp-item'})
            for vacancy in vacancy_list:
                position_info = vacancy.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'})
                position = position_info.text

                href = position_info['href']
                href_path = href[:href.find('?')]
                id = 'hh_' + href_path[href_path.rfind('/',)+1:]
                salary = vacancy.find('span', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'})
                if salary:
                    salary_text = salary.text
                    if salary_text.find('от') >= 0:
                        try:
                            salary_from = int(''.join(salary_text.replace('от', '').split()[:-1]))
                        except:
                            salary_from = None
                        salary_to = None
                    elif salary_text.find('–') >= 0:
                        sep_poz = salary_text.split().index('–')
                        try:
                            salary_from = int(''.join(salary_text.split()[:sep_poz]))
                            salary_to = int(''.join(salary_text.split()[sep_poz+1:-1]))
                        except:
                            salary_from = None
                            salary_to = None
                    elif salary_text.find('до') >= 0:
                        try:
                            salary_to = int(''.join(salary_text.replace('до', '').split()[:-1]))
                        except:
                            salary_to = None
                        salary_from = None
                    salary_currency = salary_text.split()[-1]
                else:
                    salary_from = None
                    salary_to = None
                    salary_currency = None
                source = 'hh.ru'
                d_vacancy['_id'].append(id)
                d_vacancy['position'].append(position)
                d_vacancy['href'].append(href)
                d_vacancy['salary_from'].append(salary_from)
                d_vacancy['salary_to'].append(salary_to)
                d_vacancy['salary_currency'].append(salary_currency)
                d_vacancy['source'].append(source)
    # soup.find(text='дальше').parent.parent['href']
    return pd.DataFrame.from_dict(d_vacancy)


def from_sj():
    url = 'https://russia.superjob.ru/vacancy/search/'
    d_vacancy = {
        '_id': [],
        'position': [],
        'href': [],
        'salary_from': [],
        'salary_to': [],
        'salary_currency': [],
        'source': []
    }
    for i in range(3):
        params = {
            'keywords': 'Python',
            'page': i+1
        }
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36'}

        response = requests.get(url, params=params, headers=headers)

        if response.ok:
            soup = bs(response.text, 'html.parser')
            vacancy_list = soup.find_all('div', attrs={'class': 'f-test-search-result-item'})
            for vacancy in vacancy_list:
                position_info = vacancy.find('a', attrs={'class': 'icMQ_'})
                if not position_info or 'f-test-button-V_Telegram' in position_info['class'] or 'pkcup' in position_info['class'] or not position_info.text:
                    continue
                position = position_info.text
                href = 'https://russia.superjob.ru' + position_info['href']
                href_path = href[:href.find('.html')]
                id = 'sj_' + href_path[href_path.rfind('-',)+1:]
                salary_from = None
                salary_to = None
                salary_currency = None
                salary = vacancy.find('span', attrs={'class': 'f-test-text-company-item-salary'})
                if salary:
                    salary_text = salary.text.replace('/месяц','')
                    if salary_text.find('от') >= 0:
                        try:
                            salary_from = int(''.join(salary_text.replace('от', '').split()[:-1]))
                        except:
                            salary_from = None
                        salary_to = None
                    elif salary_text.find('—') >= 0:
                        sep_poz = salary_text.split().index('—')
                        try:
                            salary_from = int(''.join(salary_text.split()[:sep_poz]))
                            salary_to = int(''.join(salary_text.split()[sep_poz+1:-1]))
                        except:
                            salary_from = None
                            salary_to = None
                    elif salary_text.find('до') >= 0:
                        try:
                            salary_to = int(''.join(salary_text.replace('до', '').split()[:-1]))
                        except:
                            salary_to = None
                        salary_from = None
                    if salary_to or salary_from:
                        salary_currency = salary_text.split()[-1]
                source = 'superjob.ru'
                d_vacancy['_id'].append(id)
                d_vacancy['position'].append(position)
                d_vacancy['href'].append(href)
                d_vacancy['salary_from'].append(salary_from)
                d_vacancy['salary_to'].append(salary_to)
                d_vacancy['salary_currency'].append(salary_currency)
                d_vacancy['source'].append(source)
    # soup.find(text='дальше').parent.parent['href']
    return pd.DataFrame.from_dict(d_vacancy)


def ex1():
    """
    1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB и реализовать функцию.
    Добавить в решение со сбором вакансий(продуктов) функцию,
    которая будет добавлять только новые вакансии/продукты в вашу базу.
    """
    df_hh = from_hh()
    df_sj = from_sj()
    df_all = df_hh.append(df_sj)

    client = MongoClient('127.0.0.1', 27017)

    db = client['vacancy_1018']
    vacancy = db.vacancy

    data_dict = df_all.to_dict("records")
    for rec in data_dict:
        try:
            vacancy.insert_one(rec)
        except dke:
            print("Already exist")


def ex2():
    """
    2. Написать функцию, которая производит поиск и выводит на экран вакансии
    с заработной платой больше введённой суммы
    (необходимо анализировать оба поля зарплаты - минимальнную и максимульную).
    """

    client = MongoClient('127.0.0.1', 27017)

    db = client['vacancy_1018']
    vacancy = db.vacancy

    salary_lvl = int(input('Желаемая ЗП от: '))

    currency_ex = {
        'USD': 71,
        'EUR': 82,
        'руб.': 1
    }

    for rec in vacancy.find({'$or': [{'salary_from': {"$gt": 0}},
                                        {'salary_to': {"$gt": 0}},
                                        ]}):
        if rec['salary_currency'] in currency_ex.keys():
            if np.nanmax(np.array([rec['salary_from'] ,rec['salary_to']], dtype=np.float64)) * currency_ex[rec['salary_currency']] > salary_lvl:
                pprint(rec)


ex1()
ex2()
