# -*- coding: utf-8 -*-
#  开发时间：2023/1/31 16:19
#  文件名称：bloom_filter.py
#  文件作者：陈梦妮
#  备注：布隆过滤器

from larkspur import ScalableBloomFilter
from rediscluster import RedisCluster

from base_tools import get_md5
from settings import startup_nodes, password

# 创建 Redis 集群连接
redis_conn = RedisCluster(
    startup_nodes=startup_nodes,
    decode_responses=False, socket_connect_timeout=30, password=password
)

sbf = ScalableBloomFilter(connection=redis_conn,
                          name='bloom_filter',
                          initial_capacity=100000000,
                          error_rate=0.0001)


def add(bl_str) -> bool:
    if isinstance(bl_str, list):
        add_many([get_md5(b) for b in bl_str])
    if isinstance(bl_str, str):
        flg = sbf.add(get_md5(bl_str))
        return flg


def add_many(bl_str_list):
    sbf.bulk_add(bl_str_list)


def is_contains(bl_str) -> bool:
    flg = sbf.__contains__(get_md5(bl_str))
    return flg


def is_contains_many(data_list):
    results = []
    for data in data_list:
        flg = is_contains(data)
        if flg:
            results.append(1)
        else:
            results.append(0)
    return results
