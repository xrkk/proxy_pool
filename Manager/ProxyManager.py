# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     ProxyManager.py
   Description :
   Author :       JHao
   date：          2016/12/3
-------------------------------------------------
   Change Activity:
                   2016/12/3:
-------------------------------------------------
"""
__author__ = 'JHao'

import random

from Util import EnvUtil
from DB.DbClient import DbClient
from Util.GetConfig import config
from Util.LogHandler import LogHandler
from Util.utilFunction import verifyProxyFormat
from ProxyGetter.getFreeProxy import GetFreeProxy


class ProxyManager(object):
    """
    ProxyManager
    """

    def __init__(self):
        self.db = DbClient()
        self.raw_proxy_queue = 'raw_proxy'
        self.log = LogHandler('proxy_manager')
        self.useful_proxy_queue = 'useful_proxy'

    def refresh(self):
        """
        fetch proxy into Db by ProxyGetter/getFreeProxy.py
        :return:
        """
        self.db.changeTable(self.raw_proxy_queue)
        # TODO: 按理说调用此函数之前已经验证过 useful_proxy 数目了, 怎么还是获取呢??
        if self.db.getNumber() >= config.max_limit:
            self.log.info("原始代理到达最大数目, 暂停获取: {}".format(config.max_limit))
            return

        for proxyGetter in config.proxy_getter_functions:
            # fetch
            try:
                self.log.info("[{func}]: 开始获取函数".format(func=proxyGetter))
                for proxy in getattr(GetFreeProxy, proxyGetter.strip())():
                    # 直接存储代理, 不用在代码中排重, hash 结构本身具有排重功能
                    proxy = proxy.strip()
                    if proxy and verifyProxyFormat(proxy):
                        # self.log.info('{func}: fetch proxy {proxy}'.format(func=proxyGetter, proxy=proxy))
                        self.db.put(proxy)
                    else:
                        self.log.error('[{func}]: 获取代理错误: {proxy}'.format(func=proxyGetter, proxy=proxy))
            except Exception as e:
                self.log.error("[{func}]: 获取代理失败".format(func=proxyGetter))
                continue

    def get(self):
        """
        return a useful proxy
        :return:
        """
        self.db.changeTable(self.useful_proxy_queue)
        item_dict = self.db.getAll()
        if item_dict:
            if EnvUtil.PY3:
                return random.choice(list(item_dict.keys()))
            else:
                return random.choice(item_dict.keys())
        return None
        # return self.db.pop()

    def delete(self, proxy):
        """
        delete proxy from pool
        :param proxy:
        :return:
        """
        self.db.changeTable(self.useful_proxy_queue)
        self.db.delete(proxy)

    def getAll(self):
        """
        get all proxy from pool as list
        :return:
        """
        self.db.changeTable(self.useful_proxy_queue)
        item_dict = self.db.getAll()
        if EnvUtil.PY3:
            return list(item_dict.keys()) if item_dict else list()
        return item_dict.keys() if item_dict else list()

    def getNumber(self):
        """
        获取原始代理和有效代理各自的数目.
        :return:
        """
        self.db.changeTable(self.raw_proxy_queue)
        total_raw_proxy = self.db.getNumber()
        self.db.changeTable(self.useful_proxy_queue)
        total_useful_queue = self.db.getNumber()
        return {'raw_proxy': total_raw_proxy, 'useful_proxy': total_useful_queue}


if __name__ == '__main__':
    pp = ProxyManager()
    pp.refresh()
