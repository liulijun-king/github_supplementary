# -*- coding: utf-8 -*-
# @Time    : 2024-04-15 9:21
# @Author  : Liu
# @Site    : 
# @File    : github.py
# @Software: PyCharm
import json
from datetime import datetime
from urllib.parse import urlparse

import dateparser
from kafka import KafkaProducer
from loguru import logger
from lxml import etree

from base_tools import json_path, get_md5
from bloom_filter import add
from instance_item import item_main
from net_tools import req_get
from redis_tools import redis_conn
from settings import id_key, day_crawl_key, retry_crawl_key, proxy, project_topic, IS_SAVA_USER, user_crawl_key


class GitHub(object):
    def __init__(self):
        self.headers = {
            'authority': 'api.github.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'accept-language': 'zh-CN,zh;q=0.9',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
        }

    def bc_id(self):
        while True:
            project_ids = redis_conn.spop(retry_crawl_key, 100)
            if len(project_ids) == 0:
                break
            for _ in project_ids:
                self.list_spider(_)

    def hava_id(self):
        while True:
            if redis_conn.llen(id_key) <= 100 or redis_conn.llen(day_crawl_key) > 200000:
                logger.info(f"今日解析完成！gb_all:day_crawl长度：{redis_conn.llen(day_crawl_key)}")
                break
            pipeline = redis_conn.pipeline()
            for _ in range(10000):
                pipeline.rpop(id_key)
            id_list = pipeline.execute()
            for _ in id_list:
                if _:
                    self.list_spider(_)

    def list_spider(self, project_id):
        try:
            project_url = f"https://api.github.com/repositories/{project_id}"
            response = req_get(project_url, headers=self.headers, proxies=proxy)
            if response.status_code == 200:
                item = item_main().copy()
                # fork的原项目ID
                item["fork_original_project"] = json_path(response.json(), '$.parent.full_name')
                # fork的根项目ID
                item["fork_root_project"] = json_path(response.json(), '$.source.full_name')
                # 项目名
                item["project_name"] = json_path(response.json(), '$.name')
                # 创建时间
                create_time = json_path(response.json(), '$.created_at')
                if create_time:
                    item["create_time"] = dateparser.parse(create_time).strftime("%Y-%m-%d %H:%M:%S")
                else:
                    logger.error(f"该文章无发布时间！ | 接口url：{response.url}")
                # 项目作者
                author = json_path(response.json(), '$.owner.login')
                item["author"] = author
                item["user_id"] = author
                # 项目标签
                tags = json_path(response.json(), '$.topics')
                item["tags"] = "#".join(tags)
                # 项目星数
                stars_count = json_path(response.json(), '$.stargazers_count')
                item["stars_count"] = str(stars_count)
                # 项目浏览数
                watch_count = json_path(response.json(), '$.subscribers_count')
                item["watch_count"] = str(watch_count)
                # 项目fork数
                forks_count = json_path(response.json(), '$.forks_count')
                item["forks_count"] = str(forks_count)
                # 项目简介
                item["abstract"] = json_path(response.json(), '$.description')
                # 项目id
                project_id = json_path(response.json(), '$.id')
                # 跳转url
                ref_url = f"https://api.github.com/repositories/{project_id}"
                item["ref_url"] = ref_url
                # uuid
                item["uuid"] = get_md5(ref_url)
                # 用户主页链接
                item["user_url"] = json_path(response.json(), '$.owner.html_url')
                # 项目url
                source_url = json_path(response.json(), '$.html_url')
                item['source_url'] = source_url
                self.entity_spider(item)
            elif response.status_code == 404:
                add(str(project_id))
            else:
                redis_conn.sadd(retry_crawl_key, str(project_id))
        except Exception as e:
            redis_conn.sadd(retry_crawl_key, str(project_id))
            logger.error(f"json页面采集失败：{e}")

    def entity_spider(self, item):
        try:
            logger.info(f"html页面采集：{item['source_url']}")
            response = req_get(item['source_url'], headers=self.headers, proxies=proxy)
            html = etree.HTML(response.content.decode())
            # 项目提交次数
            item["commit_count"] = html.xpath("//a[contains(@class,'react-last-commit-history-group')]/span")[0].xpath(
                'string(.)').replace(
                "Commits", "").strip() if html.xpath(
                "//a[contains(@class,'react-last-commit-history-group')]/span") else ""
            # 项目贡献数
            contributors_count = html.xpath("//a[contains(text(), 'Contributors')]/span")[0].xpath('string(.)').replace(
                ",", "") if html.xpath("//a[contains(text(), 'Contributors')]/span") else ""
            item["contributors_count"] = contributors_count
            # read me内容
            item["readme"] = html.xpath("//article[contains(@class,'markdown-body entry-content')]")[0].xpath(
                'string(.)') if html.xpath(
                "//article[contains(@class,'markdown-body entry-content')]") else ""
            # item["readme_html"] = response.xpath(json_path(config, "$.item_info.readme")).get("")
            # 基本信息
            item["website_name"] = 'GitHub'
            item["website_sub_name"] = 'GitHub'
            item["host"] = 'github.com'
            netloc = urlparse(response.url).netloc.replace('www.', '')
            if netloc:
                item["sub_host"] = netloc
            else:
                item["sub_host"] = item["host"]
            item['crawler_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            item['insert_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            item['update_time'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if IS_SAVA_USER:
                redis_conn.sadd(user_crawl_key, item.pop("user_url"))
            to_port(project_topic, item)
            logger.info(f"采集成功：{item['project_name']}")
        except Exception as e:
            redis_conn.sadd(retry_crawl_key, str(item['ref_url'].replace("https://api.github.com/repositories/", "")))
            logger.error(f"详情页Html解析失败：{e}")


def to_port(topic, item):
    d_count = 0
    while d_count < 3:
        try:
            send_data = json.dumps(item)
            future = kafka_pro.send(topic, send_data.encode())
            record_metadata = future.get(timeout=20)
            if record_metadata:
                add(str(item['ref_url'].replace("https://api.github.com/repositories/", "")))
                logger.info(f'插入kafka成功')
                break
        except Exception as e:
            d_count = d_count + 1
            logger.error(str(e))
    if d_count == 3:
        redis_conn.sadd(retry_crawl_key, str(item['ref_url'].replace("https://api.github.com/repositories/", "")))


if __name__ == '__main__':
    kafka_pro = KafkaProducer(
        bootstrap_servers=['172.24.73.198:9092'])
    git = GitHub()
    git.hava_id()
