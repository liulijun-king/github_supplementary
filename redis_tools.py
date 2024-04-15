# -*- coding: utf-8 -*-
# @Time    : 2024-04-15 11:08
# @Author  : Liu
# @Site    : 
# @File    : redis_tools.py
# @Software: PyCharm
from rediscluster import RedisCluster
from settings import startup_nodes, password
from settings import id_key
from loguru import logger

# 创建 Redis 集群连接
redis_conn = RedisCluster(
    startup_nodes=startup_nodes,
    decode_responses=True, socket_connect_timeout=30, password=password
)


# 添加id到redis
def add_id():
    try:
        key_len = redis_conn.llen(id_key)
        logger.info(f"redis数据库长度为{key_len}")
        count = 0
        if key_len < 1000000:
            # max_id = redis_conn.lindex(id_key, -1)
            max_id = 1000000000
            with redis_conn.pipeline() as pipe:
                for _ in range(max_id, max_id - 10000000, -1):
                    id_ = str(_)
                    pipe.lpush(id_key, id_)
                    count += 1
                    if count == 10000:
                        pipe.execute()
                        logger.info('一万个id添加完成！')
                        count = 0
    except(Exception,) as e:
        logger.error(f"添加id失败：{e}")


if __name__ == '__main__':
    add_id()
