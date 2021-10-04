import requests
import json
from pprint import pprint
from fake_useragent import UserAgent
from bs4 import BeautifulSoup as bs
import pandas as pd


def ex():
    """
    Необходимо собрать информацию о вакансиях на вводимую должность
    (используем input или через аргументы получаем должность) с сайтов HH(обязательно) и/или Superjob(по желанию).
    Приложение должно анализировать несколько страниц сайта (также вводим через input или аргументы).
    Получившийся список должен содержать в себе минимум:

    Наименование вакансии.
    Предлагаемую зарплату (разносим в три поля: минимальная и максимальная и валюта. цифры преобразуем к цифрам).
    Ссылку на саму вакансию.
    Сайт, откуда собрана вакансия.

    По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение).
    Структура должна быть одинаковая для вакансий с обоих сайтов.
    Общий результат можно вывести с помощью dataFrame через pandas.
    Сохраните в json либо csv.
    """
    df_hh = from_hh()
    df_sj = from_sj()
    df_all = df_hh.append(df_sj)
    df_all.to_csv('out.csv', index=False)


def from_hh():
    url = 'https://hh.ru/search/vacancy'
    d_vacancy = {
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
        headers = {'User-Agent': UserAgent().chrome}

        response = requests.get(url, params=params, headers=headers)

        if response.ok:
            soup = bs(response.text, 'html.parser')
            vacancy_list = soup.find_all('div', attrs={'class': 'vacancy-serp-item'})
            for vacancy in vacancy_list:
                position_info = vacancy.find('a', attrs={'data-qa': 'vacancy-serp__vacancy-title'})
                position = position_info.text
                href = position_info['href']
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
        headers = {'User-Agent': UserAgent().chrome}

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
                d_vacancy['position'].append(position)
                d_vacancy['href'].append(href)
                d_vacancy['salary_from'].append(salary_from)
                d_vacancy['salary_to'].append(salary_to)
                d_vacancy['salary_currency'].append(salary_currency)
                d_vacancy['source'].append(source)
    # soup.find(text='дальше').parent.parent['href']
    return pd.DataFrame.from_dict(d_vacancy)

ex()
