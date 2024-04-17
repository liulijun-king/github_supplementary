# -*- coding: utf-8 -*-
# @Time    : 2024-04-16 11:15
# @Author  : Liu
# @Site    : 
# @File    : git_by_search.py
# @Software: PyCharm
from urllib.parse import quote

from loguru import logger

from base_tools import read_txt
from net_tools import req_get
from redis_tools import redis_conn
from settings import proxy, retry_crawl_key


def keyword_spider(keyword):
    for page in range(1, 101):
        headers = {
            'accept': 'application/json',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'pragma': 'no-cache',
            'referer': 'https://github.com/search?q=frida&type=repositories&p=100',
            'sec-ch-ua': '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
            'x-github-target': 'dotcom',
            'x-requested-with': 'XMLHttpRequest',
        }
        try:
            params = (
                ('q', f'{quote(keyword)}'),
                ('type', 'repositories'),
                ('p', f'{page}'),
            )
            response = req_get('https://github.com/search', headers=headers, params=params, proxies=proxy)
            if response.status_code == 200 and response.json().get("payload"):
                logger.info(f"采集成功,关键词：{keyword}")
                results = response.json().get("payload").get("results")
                deal_json(results)
                if len(results) < 10:
                    break
        except Exception as e:
            logger.error(f"采集失败,当前关键词:{keyword},页码:{page},错误类型：{e}")


def deal_json(results):
    for _id in results:
        project_id = _id.get("id")
        redis_conn.sadd(retry_crawl_key, str(project_id))


if __name__ == '__main__':
    keywords = read_txt("keyword.txt")
    for k in keywords:
        keyword_spider(k)
