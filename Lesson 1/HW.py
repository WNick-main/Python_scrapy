import requests
import json
from pprint import pprint


def ex1():
    """
    1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
    сохранить JSON-вывод в файле *.json.
    """
    user = 'wnick-main'
    token = ''
    url = 'https://api.github.com/user/repos'

    responce = requests.get(url, auth=(user, token))

    if responce.ok:
        d_resp = responce.json()
        for item in d_resp:
            pprint(item.get('name'))

        with open("repos.json", "w") as repos:
            json.dump(d_resp, repos)


ex1()


def ex2():
    """
    2. Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа).
    Выполнить запросы к нему, пройдя авторизацию.
    Ответ сервера записать в файл.
    """
    user = 'wnick-main'
    token = ''
    url = 'https://api.github.com/user/repos'

    responce = requests.get(url, auth=(user, token))

    if responce.ok:
        d_resp = responce.json()
        for item in d_resp:
            pprint(item.get('name'))

        with open("repos.json", "w") as repos:
            json.dump(d_resp, repos)
            

ex2()
