# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     ProxyRefreshSchedule.py
   Description :  代理定时刷新
   Author :       JHao
   date：          2016/12/4
-------------------------------------------------
   Change Activity:
                   2016/12/4: 代理定时刷新
                   2017/03/06: 使用LogHandler添加日志
                   2017/04/26: raw_proxy_queue验证通过但useful_proxy_queue中已经存在的代理不在放入
-------------------------------------------------
"""

import sys
import time
import logging
from threading import Thread
from apscheduler.schedulers.background import BackgroundScheduler
from Util.GetConfig import config

sys.path.append('../')

from Util.utilFunction import validUsefulProxy
from Manager.ProxyManager import ProxyManager
from Util.LogHandler import LogHandler

__author__ = 'JHao'

logging.basicConfig()


class ProxyRefreshSchedule(ProxyManager):
    """
    代理定时刷新
    """

    def __init__(self):
        ProxyManager.__init__(self)
        self.log = LogHandler('refresh_schedule')

    def validProxy(self):
        """
        验证raw_proxy_queue中的代理, 将可用的代理放入useful_proxy_queue
        :return:
        """
        self.db.changeTable(self.raw_proxy_queue)
        raw_proxy_item = self.db.pop()
        # self.log.info('ProxyRefreshSchedule: [%s] 开始验证 raw_proxy' % time.ctime())
        # 计算剩余代理，用来减少重复计算
        remaining_proxies = self.getAll()
        while raw_proxy_item:
            raw_proxy = raw_proxy_item.get('proxy')
            if isinstance(raw_proxy, bytes):
                # 兼容Py3
                raw_proxy = raw_proxy.decode('utf8')

            if raw_proxy not in remaining_proxies:
                if validUsefulProxy(raw_proxy):
                    self.db.changeTable(self.useful_proxy_queue)
                    self.db.put(raw_proxy)
                    # self.log.info('ProxyRefreshSchedule: %s validation pass' % raw_proxy)
                else:
                    # self.log.info('ProxyRefreshSchedule: 验证 raw_proxy 失败: %s' % raw_proxy)
                    pass
            else:
                # self.log.info('ProxyRefreshSchedule: raw_proxy 已添加: {}'.format((raw_proxy)))
                pass
            self.db.changeTable(self.raw_proxy_queue)
            raw_proxy_item = self.db.pop()
            remaining_proxies = self.getAll()
        # self.log.info('ProxyRefreshSchedule: [%s] 验证 raw_proxy 完毕' % time.ctime())


def refreshPool():
    pp = ProxyRefreshSchedule()
    pp.validProxy()


def batchRefresh(process_num=config.refresh_process_num):
    """
    创建指定个数线程, 执行 refreshPool

    - 间隔执行的任务.
    """
    # 检验新代理
    pl = []
    for num in range(process_num):
        proc = Thread(target=refreshPool, args=())
        pl.append(proc)

    for num in range(process_num):
        pl[num].daemon = True
        pl[num].start()

    for num in range(process_num):
        pl[num].join()


def fetchAll():
    """
    根据配置文件, 获取新代理.

    - 间隔执行的任务.
    """
    p = ProxyRefreshSchedule()
    p.db.changeTable(p.useful_proxy_queue)
    if config.max_limit == 0 or p.db.getNumber() < config.max_limit:
        # 获取新代理
        p.refresh()
    else:
        p.log.fatal('有效代理到达最大数目, 暂停获取')

def run():
    scheduler = BackgroundScheduler()
    # 不用太快, 网站更新速度比较慢, 太快会加大验证压力, 导致raw_proxy积压
    scheduler.add_job(fetchAll,  'interval', seconds=config.fetch_interval, id="fetch_proxy", max_instances=1)
    scheduler.add_job(batchRefresh, "interval", seconds=config.refresh_interval, max_instances=1)  # 每分钟检查一次
    scheduler.start()

    fetchAll()

    while True:
        time.sleep(3)


if __name__ == '__main__':
    run()
