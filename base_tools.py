# -*- coding: UTF-8 -*-

import hashlib
import os
import re
import time
from datetime import datetime, timedelta
from typing import Dict, Optional

import dateparser
import requests
from jsonpath import jsonpath
from retrying import retry


def get_md5(val):
    """把目标数据进行哈希，用哈希值去重更快"""
    md5 = hashlib.md5()
    md5.update(val.encode('utf-8'))
    return md5.hexdigest()


def sha256_detail(text):
    x = hashlib.sha256()
    x.update(text.encode())
    return x.hexdigest()


def time_parse(time_text, time_style="%Y-%m-%d %H:%M:%S", url=""):
    """
    将时间换算成国际时间
    :param url: 文章url，用于报错处理
    :param time_text: 需要处理的文本
    :param time_style: 时间格式（例如：%Y-%m-%d %H:%M:%S）
    :return: 处理后的时间:str
    """
    time_final = None
    try:
        if "T" in time_text and "Z" in time_text:
            time_dt = dateparser.parse(time_text) + timedelta(hours=0)
            time_final = time_dt.strftime(time_style)
        elif "BST" in time_text or "bst" in time_text:
            time_dt = dateparser.parse(time_text) + timedelta(hours=-1)
            time_final = time_dt.strftime(time_style)
        elif "JST" in time_text or "jst" in time_text:
            time_dt = dateparser.parse(time_text) + timedelta(hours=-9)
            time_final = time_dt.strftime(time_style)
        elif "CST" in time_text:
            time_dt = dateparser.parse(time_text) + timedelta(hours=-8)
            time_final = time_dt.strftime(time_style)
        elif "EDT" in time_text or "ET" in time_text:
            time_dt = dateparser.parse(time_text) + timedelta(hours=+4)
            time_final = time_dt.strftime(time_style)
        else:
            time_dt = dateparser.parse(time_text)
            time_final = time_dt.strftime(time_style)
    except(Exception,) as e:
        print(f"时间处理发生错误！ | {str(e)} | 文章url：{url}")
        # logger.error(f"时间处理发生错误！ | {str(e)} | 文章url：{url}")
    return time_final


def time_deal(need_time):
    if re.search(r'\d{10,13}', str(need_time)):
        need_time = int(need_time)
        if len(str(need_time)) == 13:
            need_time = need_time / 1000
        time_array = time.localtime(need_time)
        other_style_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        return other_style_time
    elif re.search(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}', need_time):
        other_style_time = re.search(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}', need_time).group()
        return other_style_time
    elif re.search(r'\d{2}-\d{2}-\d{2}$', need_time):
        time_array = time.strptime(need_time, "%Y-%m-%d")
        other_style_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        return other_style_time
    elif re.search(r'\d{4}年\d{2}月\d{2}日 \d{2}:\d{2}:\d{2}$', need_time):
        time_array = time.strptime(need_time, "%Y年%m月%d日 %H:%M:%S")
        other_style_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        return other_style_time
    elif re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2}', need_time):
        need_time = re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', need_time).group()
        time_array = time.strptime(need_time, "%Y-%m-%dT%H:%M:%S")
        other_style_time = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        return other_style_time
    elif re.search(r'\d{2}/\d{2}/\d{4}\s+-\s+\d{2}:\d{2}', need_time):
        need_time = re.search(r'\d{2}/\d{2}/\d{4}\s+-\s+\d{2}:\d{2}', need_time).group()
        time_array = [n.strip() for n in need_time.split('-')]
        day_array = time_array[0].split('/')
        day_str = '-'.join(day_array[::-1])
        hour_str = time_array[1] + ':00'
        return f"{day_str} {hour_str}"
    elif re.search(r'\d{4}-\d-\d\s+\d{2}:\d{2}', need_time):
        need_time = re.search(r'\d{4}-\d-\d\s+\d{2}:\d{2}', need_time).group()
        need_time = time_parse(need_time)
        return need_time
    elif re.search(r'\d{4}年\d月\d日', need_time):
        need_time = re.search(r'\d{4}年\d月\d日', need_time).group()
        need_time = time_parse(need_time)
        return need_time
    elif re.search(r'\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}', need_time):
        need_time = re.search(r'\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}', need_time).group()
        need_time = time_parse(need_time)
        return need_time
    elif re.search(r'\d{8}', need_time):
        need_time = f"{need_time[:4]}-{need_time[4:6]}-{need_time[6:]} 00:00:00"
        return need_time
    elif re.search("\d{2}\.\d{2}\.\d{4}", need_time):
        need_time = f"{need_time[6:]}-{need_time[3:6]}-{need_time[:2]}"
        need_time = time_parse(need_time)
        return need_time
    elif re.search(r"\d{4}.\d{2}.\d{1,2}\s\d{2}.\d{2}", need_time):
        need_time = re.search(r"\d{4}.\d{2}.\d{1,2}\s\d{2}.\d{2}", need_time).group()
        need_time = time_parse(need_time)
        return need_time
    else:
        need_time = standardize_date(need_time)
        if not re.search(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", need_time):
            need_time = time_parse(need_time)
        return need_time


def standardize_date(time_str, strftime_type="%Y-%m-%d %H:%M:%S"):
    if u"刚刚" in time_str:
        time_str = datetime.now().strftime(strftime_type)
    elif u"分钟" in time_str:
        minute = time_str[:time_str.find(u"分钟")]
        minute = timedelta(minutes=int(minute))
        time_str = (datetime.now() - minute).strftime(strftime_type)
    elif u"小时" in time_str:
        hour = time_str[:time_str.find(u"小时")]
        hour = timedelta(hours=int(hour))
        time_str = (datetime.now() - hour).strftime(strftime_type.replace("%M:%S", "00:00"))
    elif u"昨天" in time_str:
        day = timedelta(days=1)
        if re.match(r"\d+:\d+", time_str):
            time_str = (datetime.now() - day).strftime("%Y-%m-%d") + time_str
        else:
            time_str = (datetime.now() - day).strftime(strftime_type.replace(" %H:%M:%S", " 00:00:00"))
    elif u"天前" in time_str:
        day_last = int(time_str[:time_str.find(u"天前")])
        day = timedelta(days=day_last)
        if re.match(r"\d+:\d+", time_str):
            time_str = (datetime.now() - day).strftime("%Y-%m-%d") + time_str
        else:
            time_str = (datetime.now() - day).strftime(strftime_type.replace(" %H:%M:%S", " 00:00:00"))
    else:
        time_str = time_str
    return time_str


def ergodic_file(base):
    all_f = []
    for root, ds, fs in os.walk(base):
        for f in fs:
            all_f.append(f"{root}/{f}")
    return all_f


def json_path(obj: Dict, expr: str, default: Optional = '', is_list: bool = False):
    """
    jsonpath解析
    :param obj: 解析对象
    :param expr: jsonpath
    :param default: 未获取到返回默认值， 默认空字符串
    :param is_list: 是否保留list， 默认不保留
    :return: 解析值或者defult
    """
    value = jsonpath(obj, expr)
    if value:
        if not is_list:
            return value[0]
        else:
            return value
    else:
        return default


def read_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        str_all = f.read()
    id_all = []
    for na in str_all.split('\n'):
        if na:
            id_all.append(na.strip())
    return list(set(id_all))
