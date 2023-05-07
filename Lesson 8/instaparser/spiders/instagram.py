import scrapy
import re
import json
from copy import deepcopy
from urllib.parse import urlencode
from scrapy.http import HtmlResponse

from instaparser.items import InstaparserItem



class InstaSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']

    inst_login_link = 'https://www.instagram.com/api/v1/web/accounts/login/ajax/'
    inst_login = 'wnick_13'   # Qw123456789
    inst_pwd = '#PWD_INSTAGRAM_BROWSER'

    user_for_parse = ['kris_t991', 'julia_serbia']
    graphql_url = 'https://www.instagram.com/graphql/query/?'
    posts_hash = 'd4d88dc1500312af6f937f7b804c68c3'
    feed_url = f'/api/v1/feed/user/'
    start_urls = ["https://instagram.com/"]

    friend_baseurl = 'https://www.instagram.com/api/v1/friendships'
    subscription_hash = 'd04b0a864b4b54837c0d870b0e77e076'
    subscriber_hash = 'c76146de99bb02f6415203be841dd25a'

    subscription_list = {}

    cookies = {
        'csrftoken': 'xbn',
        'sessionid': '118',
        'shbts': r'1683394357\',
        'rur': r'RVA\05411870137499\0541714932688:01f71c9bf7e4a483bef8e4896255d344023795654c0a29119873c6326cebf8ab5d1b79cc',
        'shbid': r'8919',
        'ig_nrcb': '1',
        'datr': '0o5W',
        'ds_user_id': '11',
        'ig_did': 'E027B59F',
        'mid': 'ZFa',

    }
    meta = {
        'dont_redirect': False,
        'handle_httpstatus_list': [400],
        'download_timeout': 10,
    }

    #def start_requests(self):
    #    for url in InstaSpider.start_urls:
    #        yield Request(url=url, callback=InstaSpider.parse, cookies=InstaSpider.cookies) # get_headers(self.inst_login)meta=self.meta,

    def parse(self, response: HtmlResponse):
        csrf = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.inst_login_link,
            method='POST',
            callback=self.login_parse,
            formdata={'username': self.inst_login,
                      'enc_password': self.inst_pwd},
            headers={'X-CSRFToken': csrf}
        )

    def login_parse(self, response: HtmlResponse):
        j_data = response.json()
        if j_data['authenticated']:
            for user in self.user_for_parse:
                yield response.follow(
                    f'/{deepcopy(user)}',
                    callback=self.user_parse,
                    cb_kwargs={'username': deepcopy(user)}
                )
        print()

    def user_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        variables = {"id": user_id,
                     "first": 25}
        self.subscription_list[deepcopy(user_id)] = []
        url_friend = f'{self.graphql_url}query_hash={self.subscriber_hash}&variables=' + json.dumps(variables,
                                                                                                    separators=(
                                                                                                        ',', ':'))
        #url_friend = f'{self.friend_baseurl}/{user_id}/followers/?{urlencode(variables)}'
        #url_posts = f'{self.graphql_url}query_hash={self.posts_hash}&{urlencode(variables)}'
        #url_posts = f'{self.feed_url}{username}/username/?{urlencode(variables)}'
        yield response.follow(url_friend,
                              callback=self.user_info_parse,
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'variables': deepcopy(variables),
                                         'item_type': 'friend'}
                              )

        url_subscr = f'{self.graphql_url}query_hash={self.subscription_hash}&variables=' + json.dumps(variables,
                                                                                                    separators=(
                                                                                                        ',', ':'))
        yield response.follow(url_subscr,
                              callback=self.user_info_parse,
                              cb_kwargs={'username': username,
                                         'user_id': user_id,
                                         'variables': deepcopy(variables),
                                         'item_type': 'subscr'}
                              )

    def user_info_parse(self, response: HtmlResponse, username, user_id, variables, item_type):
        j_data = json.loads(response.text)

        if item_type == 'friend':
            user_info = j_data.get('data').get('user').get('edge_followed_by')
            posts_hash = self.subscriber_hash
        else:
            user_info = j_data.get('data').get('user').get('edge_follow')
            posts_hash = self.subscription_hash

        users = user_info.get('edges')
        for user in users:
            item = InstaparserItem(
                user_id=user['node']['id'],
                photo=user['node']['profile_pic_url'],
                fullname=user['node']['full_name'],
                username=user['node']['username'],
                connect_to=user_id,
                connect_kind=item_type
            )
            yield item

        if user_info.get('page_info').get('has_next_page'):
            variables['after'] = user_info['page_info']['end_cursor']
            url_posts = f'{self.graphql_url}query_hash={posts_hash}&{urlencode(variables)}'
            yield response.follow(
                url_posts,
                callback=self.user_info_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables),
                           'item_type': item_type}
            )

    def fetch_csrf_token(self, text):
        ''' Get csrf-token for auth '''
        matched = re.search(r'\"csrf_token\":\"\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        matched = re.search(r'\"id\":\"\d+\"', text).group()
        return json.loads("{"+matched+"}").get('id')
