CREATE USER srv_scrapy with password 'scrapypass';

CREATE schema scrapy;

GRANT ALL ON SCHEMA scrapy TO srv_scrapy;

drop table if exists scrapy.insta_users;
drop table if exists scrapy.insta_user_connect;

create table scrapy.insta_users (user_id text PRIMARY KEY, photo text, username text, fullname text);
create table scrapy.insta_user_connect (conn_id text PRIMARY KEY, user_id text, subscr_user_id text);

GRANT TRUNCATE, UPDATE, DELETE, SELECT, INSERT, TRIGGER, REFERENCES ON TABLE scrapy.insta_users TO srv_scrapy;
GRANT TRUNCATE, UPDATE, DELETE, SELECT, INSERT, TRIGGER, REFERENCES ON TABLE scrapy.insta_user_connect TO srv_scrapy;

select * from scrapy.insta_users;

select * from scrapy.insta_user_connect;

delete from scrapy.insta_users;

delete from scrapy.insta_user_connect;

-- На кого подписан пользователь 57456559902
select distinct info.username, info.fullname
from scrapy.insta_users info
	inner join scrapy.insta_user_connect conn
		on conn.user_id = '57456559902'
		and info.user_id = conn.subscr_user_id
			
-- Кто подписан на пользователя 57456559902
select distinct info.username, info.fullname
from scrapy.insta_users info
	inner join scrapy.insta_user_connect conn
		on conn.subscr_user_id = '57456559902'
		and info.user_id = conn.user_id