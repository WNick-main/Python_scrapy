# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import psycopg2

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class JobparserPipeline:
    def __init__(self):
        self.db_conn = psycopg2.connect(database="scrapy", user="srv_spider",
                                        password="spider_pass", host="localhost", port=5432)

    def process_item(self, item, spider):

        item['salary_min'], item['salary_max'], item['currency'] = self.process_salary(item['salary'], spider.name)
        raw_salary = '-'.join(item['salary'])
        cur = self.db_conn.cursor()
        cur.execute(
            f'''INSERT INTO vacancies_{spider.name} (url, name, raw_salary, salary_from, salary_to, currency) 
            VALUES ('{item['url']}', '{item['title']}', '{raw_salary}', {item['salary_min']}, {item['salary_max']}, '{item['currency']}')''')
        self.db_conn.commit()
        cur.close()
        return item

    def process_salary(self, raw_salary, source):
        salary_from = '0'
        salary_to = '0'
        currency = ''
        if source == 'hhru':
            if raw_salary[0] == 'от ':
                salary_from = raw_salary[1].replace('\xa0', '')
                if raw_salary[2] == ' до ':
                    salary_to = raw_salary[3].replace('\xa0', '')
                    currency = raw_salary[5]
                else:
                    salary_to = 0
                    currency = raw_salary[3]
            elif raw_salary[0] == 'до ':
                salary_from = 0
                salary_to = raw_salary[1].replace('\xa0', '')
                currency = raw_salary[3]
        elif source == 'sjru':
            if raw_salary[0] == 'от':
                salary_from = raw_salary[2].replace('\xa0', '').replace('₽', '')
                if raw_salary[2] == ' до ':
                    salary_to = raw_salary[3].replace('\xa0', '').replace('₽', '')
                    currency = 'руб.' if raw_salary[2][-1:] == '₽' else ''
                else:
                    salary_to = 0
                    currency = 'руб.' if raw_salary[2][-1:] == '₽' else ''
            if raw_salary[0] == 'до':
                salary_to = raw_salary[2].replace('\xa0', '').replace('₽', '')
                currency = 'руб.' if raw_salary[2][-1:] == '₽' else ''
            elif raw_salary[0] == 'По договорённости':
                pass
            elif raw_salary[2] == '₽':
                salary_from = raw_salary[0].replace('\xa0', '').replace('₽', '')
                salary_to = raw_salary[0].replace('\xa0', '').replace('₽', '')
                currency = 'руб.' if raw_salary[2][-1:] == '₽' else ''
            elif raw_salary[2] == '—':
                salary_from = raw_salary[0].replace('\xa0', '').replace('₽', '')
                salary_to = raw_salary[4].replace('\xa0', '').replace('₽', '')
                currency = 'руб.' if raw_salary[6][-1:] == '₽' else ''
        return salary_from, salary_to, currency
