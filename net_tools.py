# -*- coding: utf-8 -*-
# @Time    : 2024-04-15 10:57
# @Author  : Liu
# @Site    : 
# @File    : net_tools.py
# @Software: PyCharm

import requests
from retrying import retry


def retry_error(exception):
    return isinstance(exception, Exception)


@retry(retry_on_exception=retry_error, stop_max_attempt_number=5, wait_fixed=500)
def req_get(url, headers, params=None, cookies=None, proxies=None, verify=True, stream=None):
    response = requests.get(url=url, headers=headers, params=params, verify=verify, cookies=cookies,
                            proxies=proxies, stream=stream, timeout=10)
    return response


@retry(retry_on_exception=retry_error, stop_max_attempt_number=5, wait_fixed=500)
def req_post(url, headers=None, data=None, params=None, verify=True, cookies=None, proxies=None,
             json_data=None):
    response = requests.get(url=url, headers=headers, data=data, params=params, verify=verify, cookies=cookies,
                            timeout=10,
                            proxies=proxies, json=json_data)
    return response




