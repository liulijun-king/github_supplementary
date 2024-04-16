# -*- coding: utf-8 -*-
# @Time    : 2024-04-15 11:10
# @Author  : Liu
# @Site    : 
# @File    : settings.py
# @Software: PyCharm

# redis键名配置
id_key = 'gb_all_b:ids'
day_crawl_key = 'gb_all_b:day_crawl'
retry_crawl_key = 'gb_all_b:retry_crawl'
user_crawl_key = 'gb_all_b:user_crawl'

# redis项目信息
startup_nodes = [
    {"host": "120.55.67.165", "port": 6379},
    {"host": "120.26.85.177", "port": 6379}
]
password = 'gew29YAyi'

# 代理信息
proxy = "http://f2199815664-region-US-period-0:k0sl96zx@us.r618.kdlfps.com:18866/"

# 推送topic
project_topic = "topic_c1_original_github_projectinformation"

# 是否采集用户项目
IS_SAVA_USER = False
