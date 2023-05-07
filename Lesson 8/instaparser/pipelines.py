# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import psycopg2


class InstaparserPipeline:
    def __init__(self):
        self.db_conn = psycopg2.connect(database="main", user="srv_scrapy",
                                        password="scrapypass", host="localhost", port=5432)

    def process_item(self, item, spider):
        cur = self.db_conn.cursor()

        sql_main_info = f'''INSERT INTO scrapy.insta_users (user_id, photo, username, fullname) VALUES ('{item['user_id']}', '{item['photo']}', '{item['username']}', '{item['fullname']}')'''
        '''Добавляем связи пользователь - подписчик'''
        if item['connect_kind'] == 'friend':
            user = item['user_id']
            subscr_user = item['connect_to']
        else:
            user = item['connect_to']
            subscr_user = item['user_id']
        conn_id = user + subscr_user
        sql_subscr = f'''INSERT INTO scrapy.insta_user_connect (conn_id, user_id, subscr_user_id) VALUES ('{conn_id}', '{user}', '{subscr_user}')'''
        try:
            cur.execute(sql_subscr)
            self.db_conn.commit() # Связь нужна всегда, даже если не выполняется unique констрейнт для информации
            cur.execute(sql_main_info)
            self.db_conn.commit()
        except psycopg2.errors.UniqueViolation as e:
            self.db_conn.rollback()
        except Exception as e:
            print(e)
            self.db_conn.rollback()
        finally:
            cur.close()
        return item
