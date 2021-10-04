import requests
import json
from pprint import pprint


def ex():
    """
    1. Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев для конкретного пользователя,
    сохранить JSON-вывод в файле *.json.
    2. Изучить список открытых API. Найти среди них любое, требующее авторизацию (любого типа).
    Выполнить запросы к нему, пройдя авторизацию.
    Ответ сервера записать в файл.
    """
    user = 'wnick-main'
    token = ''
    url = 'https://api.github.com/user/repos'

    response = requests.get(url, auth=(user, token))

    if response.ok:
        d_resp = response.json()
        for item in d_resp:
            pprint(item.get('name'))

        with open("repos.json", "w") as repos:
            json.dump(d_resp, repos)


ex()

