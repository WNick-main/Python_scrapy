from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as dke
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
import time


client = MongoClient('127.0.0.1', 27017)
db = client['pepper_db']
pepper_adv = db.pepper_adv


chrome_options = Options()
# chrome_options.add_argument("start-maximized")

url = 'https://www.pepper.ru/'

driver = webdriver.Chrome(options=chrome_options)
driver.get(url)

for i in range(10):
    articles = driver.find_elements(By.TAG_NAME, 'article')
    actions = ActionChains(driver)
    actions.move_to_element(articles[-1])
    actions.perform()
    time.sleep(3)

items_list = []
articles = driver.find_elements(By.TAG_NAME, 'article')
for art in articles:
    if art.get_attribute('data-t') == 'telegramWidget':
        continue
    art_dict = {}
    try:
        vote_box = art.find_element(By.XPATH, ".//div[contains(@class,'vote-box')]/span")
        art_dict['art_rate'] = vote_box.text
    except NoSuchElementException:
        art_dict['art_rate'] = '-'
    try:
        art_dict['art_price'] = art.find_element(By.XPATH, ".//span[contains(@class,'thread-price')]").text
    except NoSuchElementException:
        art_dict['art_price'] = '-'
    art_dict['art_title'] = art.find_element(By.XPATH, ".//strong[contains(@class,'thread-title')]").text
    art_dict['art_ref'] = art.find_element(By.TAG_NAME, "a").get_attribute("href")

    items_list.append(art_dict)

    try:
        pepper_adv.insert_one(art_dict)
        pepper_adv.create_index('Link', unique=True)
    except dke:
        continue


driver.quit()


