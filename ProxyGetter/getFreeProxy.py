# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     GetFreeProxy.py
   Description :  抓取免费代理
   Author :       JHao
   date：          2016/11/25
-------------------------------------------------
   Change Activity:
                   2016/11/25:
-------------------------------------------------



"""
import re
import sys
import requests

sys.path.append('..')

from Util.WebRequest import WebRequest
from Util.utilFunction import getHtmlTree

from scrapy.http import TextResponse

# for debug to disable insecureWarning
requests.packages.urllib3.disable_warnings()

from Util.LogHandler import LogHandler

logggg = LogHandler('getFreeProxy')

"""
原版的[墙内]:
    66ip.cn
    xdaili.cn
    iphai.com
    ip181.com                              # 无效                           
    ip3366.net
    data5u.com
    mimiip.com
    xicidaili.com
    goubanjia.com
    kuaidaili.com
    coderbusy.com
    jiangxianli.com
增加的[墙内]:
    31f.cn                                  http://31f.cn/                                         # 60m # 01 Yes
    89ip.cn                                 http://www.89ip.cn/                                    # 15m # 02 Yes
    zdaye.com                               http://ip.zdaye.com/FreeIPlist.html                    # 端口为图片
    waitig.com                              https://www.waitig.com/proxy/                          # 1年多没更新啦
    horocn.com                              https://proxy.horocn.com/free-proxy.html               # 端口为图片
    swei360.com                             http://www.swei360.com/                                # 更新太慢, 网站访问速度也很慢
    proxyhub.me                             https://www.proxyhub.me/zh/all-free-proxy-list.html    # 在 cookie 中设置 page, 而且不知道更新频率
    seofangfa.com                           http://ip.seofangfa.com/                               # 01d? # 03 Yes
    ipaddress.com                           https://www.ipaddress.com/proxy-list/                  # 检测间隔太长
    cool-proxy.net                          https://www.cool-proxy.net/proxies/http_proxy_list/sort:update_time/direction:desc  # 实时 # 04 Yes # 近200页, 间隔大概30分钟
    mrhinkydink.com                         http://www.mrhinkydink.com/proxies.htm                 # 检测间隔太长
    https://github.com/a2u/free-proxy-list                             # 1小时更新1次
    https://github.com/clarketm/proxy-list/blob/master/proxy-list.txt  # 1天更新1次
原版的[墙外]:
    cn-proxy.com
    proxy-list.org
    list.proxylistplus.com
增加的[墙外]:
    spys.one                                http://spys.one/en/free-proxy-list/                    # 检测间隔略长
    xroxy.com                               https://www.xroxy.com/free-proxy-lists/                # 01
    hidemyna.me                             https://hidemyna.me/en/proxy-list/                     # 有机器人检测, 直接获取的为脚本
    hidester.com                            https://hidester.com/proxylist/
    free-proxy.cz                           http://free-proxy.cz/en/                               # ?? 间隔几小时, 前5页可访问, 后面就验证机器人了
    httptunnel.ge                           http://www.httptunnel.ge/ProxyListForFree.aspx
    proxyhttp.net                           https://proxyhttp.net/
    proxynova.com                           https://www.proxynova.com/proxy-server-list/country-cn/    https://www.proxynova.com/proxy-server-list/
    hide-my-ip.com                          https://www.hide-my-ip.com/proxylist.shtml             # ip在源码的脚本部分, 但是提取不出来
    gatherproxy.com                         http://www.gatherproxy.com/                            # 02
    freeproxylists.net                      http://www.freeproxylists.net/zh/                      # ?? 不能按验证时间排序 150页左右 机器人验证
    free-proxy-list.net                     https://free-proxy-list.net/                           # 03
"""


class GetFreeProxy(object):
    """
    proxy getter
    """

    @staticmethod
    def freeProxyFirst(page=10):
        """
        无忧代理 http://www.data5u.com/
        几乎没有能用的
        :param page: 页数
        :return:
        """
        url_list = [
            'http://www.data5u.com/',
            'http://www.data5u.com/free/gngn/index.shtml',
            'http://www.data5u.com/free/gnpt/index.shtml'
        ]
        for url in url_list:
            html_tree = getHtmlTree(url)
            ul_list = html_tree.xpath('//ul[@class="l2"]')
            for ul in ul_list:
                try:
                    yield ':'.join(ul.xpath('.//li/text()')[0:2])
                except Exception as e:
                    print(e)

    @staticmethod
    def freeProxySecond(area=33, page=1):
        """
        代理66 http://www.66ip.cn/
        :param area: 抓取代理页数，page=1北京代理页，page=2上海代理页......
        :param page: 翻页
        :return:
        """
        area = 33 if area > 33 else area
        for area_index in range(1, area + 1):
            for i in range(1, page + 1):
                url = "http://www.66ip.cn/areaindex_{}/{}.html".format(area_index, i)
                html_tree = getHtmlTree(url)
                tr_list = html_tree.xpath("//*[@id='footer']/div/table/tr[position()>1]")
                if len(tr_list) == 0:
                    continue
                for tr in tr_list:
                    yield tr.xpath("./td[1]/text()")[0] + ":" + tr.xpath("./td[2]/text()")[0]
                break

    @staticmethod
    def freeProxyThird(days=1):
        """
        ip181 http://www.ip181.com/  不能用了
        :param days:
        :return:
        """
        url = 'http://www.ip181.com/'
        html_tree = getHtmlTree(url)
        try:
            tr_list = html_tree.xpath('//tr')[1:]
            for tr in tr_list:
                yield ':'.join(tr.xpath('./td/text()')[0:2])
        except Exception as e:
            pass

    @staticmethod
    def freeProxyFourth(page_count=2):
        """
        西刺代理 http://www.xicidaili.com
        :return:
        """
        url_list = [
            'http://www.xicidaili.com/nn/',  # 高匿
            'http://www.xicidaili.com/nt/',  # 透明
            'http://www.xicidaili.com/wn/',  # HTTPS
            'http://www.xicidaili.com/wt/',  # HTTP
        ]
        for each_url in url_list:
            for i in range(1, page_count + 1):
                page_url = each_url + str(i)
                tree = getHtmlTree(page_url)
                proxy_list = tree.xpath('.//table[@id="ip_list"]//tr[position()>1]')
                for proxy in proxy_list:
                    try:
                        yield ':'.join(proxy.xpath('./td/text()')[0:2])
                    except Exception as e:
                        pass

    @staticmethod
    def freeProxyFifth():
        """
        guobanjia http://www.goubanjia.com/
        :return:
        """
        url = "http://www.goubanjia.com/"
        tree = getHtmlTree(url)
        proxy_list = tree.xpath('//td[@class="ip"]')
        # 此网站有隐藏的数字干扰，或抓取到多余的数字或.符号
        # 需要过滤掉<p style="display:none;">的内容
        xpath_str = """.//*[not(contains(@style, 'display: none'))
                                        and not(contains(@style, 'display:none'))
                                        and not(contains(@class, 'port'))
                                        ]/text()
                                """
        for each_proxy in proxy_list:
            try:
                # :符号裸放在td下，其他放在div span p中，先分割找出ip，再找port
                ip_addr = ''.join(each_proxy.xpath(xpath_str))
                port = each_proxy.xpath(".//span[contains(@class, 'port')]/text()")[0]
                yield '{}:{}'.format(ip_addr, port)
            except Exception as e:
                pass

    @staticmethod
    def freeProxySixth():
        """
        讯代理 http://www.xdaili.cn/
        :return:
        """
        url = 'http://www.xdaili.cn/ipagent/freeip/getFreeIps?page=1&rows=10'
        request = WebRequest()
        try:
            res = request.get(url, timeout=10).json()
            for row in res['RESULT']['rows']:
                yield '{}:{}'.format(row['ip'], row['port'])
        except Exception as e:
            pass

    @staticmethod
    def freeProxySeventh():
        """
        快代理 https://www.kuaidaili.com
        """
        url_list = [
            'https://www.kuaidaili.com/free/inha/{page}/',
            'https://www.kuaidaili.com/free/intr/{page}/'
        ]
        for url in url_list:
            for page in range(1, 2):
                page_url = url.format(page=page)
                tree = getHtmlTree(page_url)
                proxy_list = tree.xpath('.//table//tr')
                for tr in proxy_list[1:]:
                    yield ':'.join(tr.xpath('./td/text()')[0:2])

    @staticmethod
    def freeProxyEight():
        """
        秘密代理 http://www.mimiip.com
        """
        url_gngao = ['http://www.mimiip.com/gngao/%s' % n for n in range(1, 2)]  # 国内高匿
        url_gnpu = ['http://www.mimiip.com/gnpu/%s' % n for n in range(1, 2)]  # 国内普匿
        url_gntou = ['http://www.mimiip.com/gntou/%s' % n for n in range(1, 2)]  # 国内透明
        url_list = url_gngao + url_gnpu + url_gntou

        request = WebRequest()
        for url in url_list:
            r = request.get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\w\W].*<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ':'.join(proxy)

    @staticmethod
    def freeProxyNinth():
        """
        码农代理 https://proxy.coderbusy.com/
        :return:
        """
        urls = ['https://proxy.coderbusy.com/classical/country/cn.aspx?page=1']
        request = WebRequest()
        for url in urls:
            r = request.get(url, timeout=10)
            proxies = re.findall('data-ip="(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})".+?>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ':'.join(proxy)

    @staticmethod
    def freeProxyTen():
        """
        云代理 http://www.ip3366.net/free/
        :return:
        """
        urls = ['http://www.ip3366.net/free/']
        request = WebRequest()
        for url in urls:
            r = request.get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ":".join(proxy)

    @staticmethod
    def freeProxyEleven():
        """
        IP海 http://www.iphai.com/free/ng
        :return:
        """
        urls = [
            'http://www.iphai.com/free/ng',
            'http://www.iphai.com/free/np',
            'http://www.iphai.com/free/wg',
            'http://www.iphai.com/free/wp'
        ]
        request = WebRequest()
        for url in urls:
            r = request.get(url, timeout=10)
            proxies = re.findall(r'<td>\s*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*?</td>[\s\S]*?<td>\s*?(\d+)\s*?</td>',
                                 r.text)
            for proxy in proxies:
                yield ":".join(proxy)

    @staticmethod
    def freeProxyTwelve(page_count=2):
        """
        guobanjia http://ip.jiangxianli.com/?page=
        免费代理库
        超多量
        :return:
        """
        for i in range(1, page_count + 1):
            url = 'http://ip.jiangxianli.com/?page={}'.format(i)
            html_tree = getHtmlTree(url)
            tr_list = html_tree.xpath("/html/body/div[1]/div/div[1]/div[2]/table/tbody/tr")
            if len(tr_list) == 0:
                continue
            for tr in tr_list:
                yield tr.xpath("./td[2]/text()")[0] + ":" + tr.xpath("./td[3]/text()")[0]

    @staticmethod
    def freeProxy01():
        """
        31f.cn

        - 登陆能获取更多, 但网站注册登陆系统有问题.
        - 通过 /region/xxx 来多获取一些
            - region_list = r.xpath("//table[@class='table table-bordered']")[0].xpath("//td/a[contains(@href,'/region/')]/@href").extract()
            - region_set = set(region_list)
            - 只保留代理更新比较频繁的区域
        """
        urls = [
            'http://31f.cn/',
            'http://31f.cn/region/上海/',
            # 'http://31f.cn/region/云南/',
            # 'http://31f.cn/region/内蒙古/',
            'http://31f.cn/region/北京/',
            # 'http://31f.cn/region/吉林/',
            # 'http://31f.cn/region/四川/',
            # 'http://31f.cn/region/天津/',
            # 'http://31f.cn/region/宁夏/',
            'http://31f.cn/region/安徽/',
            # 'http://31f.cn/region/山东/',
            # 'http://31f.cn/region/山西/',
            'http://31f.cn/region/广东/',
            # 'http://31f.cn/region/广西/',
            # 'http://31f.cn/region/新疆/',
            'http://31f.cn/region/江苏/',
            # 'http://31f.cn/region/江西/',
            # 'http://31f.cn/region/河北/',
            # 'http://31f.cn/region/河南/',
            # 'http://31f.cn/region/浙江/',
            # 'http://31f.cn/region/海南/',
            # 'http://31f.cn/region/湖北/',
            # 'http://31f.cn/region/湖南/',
            # 'http://31f.cn/region/甘肃/',
            # 'http://31f.cn/region/福建/',
            # 'http://31f.cn/region/西藏/',
            # 'http://31f.cn/region/贵州/',
            # 'http://31f.cn/region/辽宁/',
            # 'http://31f.cn/region/重庆/',
            # 'http://31f.cn/region/陕西/',
            # 'http://31f.cn/region/青海/',
            # 'http://31f.cn/region/黑龙江/',
        ]
        r = WebRequest()
        for url in urls:

            tree = TextResponse(url, body=r.get(url).text, encoding='utf-8')
            for el in tree.xpath("//table[@class='table table-striped']/tr")[1:]:
                try:
                    ip_addr = el.xpath(".//td[2]/text()").extract_first().strip()
                    port = el.xpath(".//td[3]/text()").extract_first().strip()
                    yield '{}:{}'.format(ip_addr, port)
                except Exception as e:
                    # logggg.error('freeProxy01 - {}'.format(e.args))
                    pass

    @staticmethod
    def freeProxy02():
        """
        89ip.cn

        - 15m
        """
        urls = ['http://www.89ip.cn/index_{}.html'.format(i) for i in range(1, 8)]
        r = WebRequest()
        for url in urls:

            tree = TextResponse(url, body=r.get(url).text, encoding='utf-8')
            for el in tree.xpath("//table[@class='layui-table']/tbody/tr"):
                try:
                    ip_addr = el.xpath(".//td[1]/text()").extract_first().strip()
                    port = el.xpath(".//td[2]/text()").extract_first().strip()
                    yield '{}:{}'.format(ip_addr, port)
                except Exception as e:
                    # logggg.error('freeProxy02 - {}'.format(e.args))
                    pass

    @staticmethod
    def freeProxy03():
        """
        ip.seofangfa.com

        - 其他页面是几年以前的了
        """
        urls = ['http://ip.seofangfa.com/']
        r = WebRequest()
        for url in urls:

            tree = TextResponse(url, body=r.get(url).text, encoding='utf-8')
            for el in tree.xpath("//table[@class='table']/tbody/tr"):
                try:
                    ip_addr = el.xpath(".//td[1]/text()").extract_first().strip()
                    port = el.xpath(".//td[2]/text()").extract_first().strip()
                    yield '{}:{}'.format(ip_addr, port)
                except Exception as e:
                    # logggg.error('freeProxy03 - {}'.format(e.args))
                    pass

    @staticmethod
    def freeProxy04():
        """
        cool-proxy.net

        -
        """
        import base64
        import codecs
        dr = codecs.getdecoder("rot-13")

        urls = ['https://www.cool-proxy.net/proxies/http_proxy_list/sort:update_time/direction:desc/page:{}'.format(i) for i in range(1, 50)]
        r = WebRequest()
        try:
            for url in urls:

                rr = r.get(url)
                tree = TextResponse(url, body=rr.text, encoding='utf-8')
                for el in tree.xpath("//table/tr")[1:]:
                    try:
                        # document.write(Base64.decode(str_rot13("ZGp3YwHmYwphAQV=")))
                        ip_addr_sec = el.xpath(".//td[1]/script/text()").extract_first().strip().split("\"")[1]
                        ip_addr = base64.b64decode(dr(ip_addr_sec)[0]).decode('utf-8')
                        port = el.xpath(".//td[2]/text()").extract_first().strip()
                        yield '{}:{}'.format(ip_addr, port)
                    except Exception as e1:
                        # logggg.error('freeProxy04 - {}'.format(e1.args))
                        pass
        except Exception as e:
            # logggg.error('freeProxy04 - {}'.format(e.args))
            pass

    @staticmethod
    def freeProxyWallFirst():
        """
        墙外网站 cn-proxy
        :return:
        """
        urls = ['http://cn-proxy.com/', 'http://cn-proxy.com/archives/218']
        request = WebRequest()
        for url in urls:
            r = request.get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\w\W]<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ':'.join(proxy)

    @staticmethod
    def freeProxyWallSecond():
        """
        https://proxy-list.org/english/index.php
        :return:
        """
        urls = ['https://proxy-list.org/english/index.php?p=%s' % n for n in range(1, 10)]
        request = WebRequest()
        import base64
        for url in urls:
            r = request.get(url, timeout=10)
            proxies = re.findall(r"Proxy\('(.*?)'\)", r.text)
            for proxy in proxies:
                yield base64.b64decode(proxy).decode()

    @staticmethod
    def freeProxyWallThird():
        urls = ['https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1']
        request = WebRequest()
        for url in urls:
            r = request.get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ':'.join(proxy)

    @staticmethod
    def freeProxyWall01():
        """
        https://www.xroxy.com/free-proxy-lists/

        - 不知道验证时间
        """
        urls = ['https://www.xroxy.com/free-proxy-lists/']
        r = WebRequest()
        for url in urls:

            try:
                rr = r.get(url)
                tree = TextResponse(url, body=rr.text, encoding='utf-8')
                for el in tree.xpath("//table[@id='DataTables_Table_0']/tbody/tr")[1:-1]:
                    try:
                        ip_addr = el.xpath(".//td[1]/text()").extract_first().strip()
                        port = el.xpath(".//td[2]/text()").extract_first().strip()
                        yield '{}:{}'.format(ip_addr, port)
                    except Exception as e1:
                        # logggg.error('freeProxyWall01 - {}'.format(e1.args))
                        pass

            except Exception as e:
                # logggg.error('freeProxyWall01 - {}'.format(e1.args))
                pass

    # @staticmethod
    # def freeProxyWall02():
    #     """
    #     free-proxy.cz
    #
    #     - 第6页开始验证机器人
    #     """
    #     import base64
    #     urls = ['http://free-proxy.cz/en/proxylist/main/date/{}'.format(i) for i in range(1, 6)]
    #     r = WebRequest()
    #     for url in urls:
    #
    #         try:
    #             rr = r.get(url, {'cookie':'p=710bbc6caad6a01a99555f056f1f10b2; __utmc=104525399; __utmz=104525399.1543376826.2.2.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __utma=104525399.1099477816.1543374610.1543376826.1543388254.3; __utmt=1; __utmb=104525399.13.10.1543388254'})
    #             tree = TextResponse(url, body=rr.text, encoding='utf-8')
    #             for el in tree.xpath("//table[@id='proxy_list']/tbody/tr")[1:-1]:
    #                 try:
    #                     # document.write(Base64.decode("MTA5LjIzMy4xMjYuNDg="))
    #                     ip_addr_sec = el.xpath(".//td[1]/abbr/script/text()").extract_first().strip().split("\"")[1]
    #                     ip_addr = base64.b64decode(ip_addr_sec).decode('utf-8')
    #                     port = el.xpath(".//td[2]/span/text()").extract_first().strip()
    #                     yield '{}:{}'.format(ip_addr, port)
    #                 except Exception as e1:
    #                     # logggg.error('freeProxyWall02 - {}'.format(e1.args))
    #                     pass
    #
    #         except Exception as e:
    #             # logggg.error('freeProxyWall02 - {}'.format(e1.args))
    #             pass

    @staticmethod
    def freeProxyWall02():
        """
        http://www.gatherproxy.com/

        -
        """
        import json
        urls = ['http://www.gatherproxy.com/']
        r = WebRequest()
        for url in urls:

            try:
                rr = r.get(url)
                tree = TextResponse(url, body=rr.text, encoding='utf-8')
                for el in tree.xpath("//script[contains(text(),'gp.insertPrx')]"):
                    try:
                        script_txt = el.xpath(".//text()").extract_first().strip()
                        j = json.loads(script_txt.split('(')[1][:-2])
                        ip_addr = j.get('PROXY_IP')
                        port = int(j.get('PROXY_PORT'), 16)
                        yield '{}:{}'.format(ip_addr, port)
                    except Exception as e1:
                        # logggg.error('freeProxyWall02 - {}'.format(e1.args))
                        pass

            except Exception as e:
                # logggg.error('freeProxyWall02 - {}'.format(e1.args))
                pass

    # @staticmethod
    # def freeProxyWall03():
    #     """
    #     http://www.freeproxylists.net/zh/
    #
    #     - 不能按验证时间排序
    #     - %3c%61%20%68%72%65%66%3d%22%68%74%74%70%3a%2f%2f%77%77%77%2e%66%72%65%65%70%72%6f%78%79%6c%69%73%74%73%2e%6e%65%74%2f%7a%68%2f%31%31%38%2e%31%37%35%2e%31%37%36%2e%31%33%35%2e%68%74%6d%6c%22%3e%31%31%38%2e%31%37%35%2e%31%37%36%2e%31%33%35%3c%2f%61%3e
    #     - urllib.parse.unquote(x) -> '<a href="http://www.freeproxylists.net/zh/118.175.176.135.html">118.175.176.135</a>'
    #     - x.split('>')[1][:-3]
    #     """
    #     urls = ['http://www.freeproxylists.net/zh/?s=u&page={}'.format(i) for i in range(2, 50)]
    #     urls.insert(0, 'http://www.freeproxylists.net/zh/?s=u')
    #     r = WebRequest()
    #     for url in urls:
    #
    #         try:
    #             rr = r.get(url)
    #             tree = TextResponse(url, body=rr.text, encoding='utf-8')
    #             for el in tree.xpath("//script[contains(text(),'gp.insertPrx')]"):
    #                 try:
    #                     script_txt = el.xpath(".//text()").extract_first().strip()
    #                     j = json.loads(script_txt.split('(')[1][:-2])
    #                     ip_addr = j.get('PROXY_IP')
    #                     port = int(j.get('PROXY_PORT'), 16)
    #                     yield '{}:{}'.format(ip_addr, port)
    #                 except Exception as e1:
    #                     # logggg.error('freeProxyWall02 - {}'.format(e1.args))
    #                     pass
    #
    #         except Exception as e:
    #             # logggg.error('freeProxyWall02 - {}'.format(e1.args))
    #             pass

    @staticmethod
    def freeProxyWall03():
        """
        free-proxy-list.net

        -
        """
        import json
        urls = [
            'https://free-proxy-list.net/',
            'https://www.us-proxy.org/'
        ]
        r = WebRequest()
        for url in urls:

            try:
                rr = r.get(url)
                tree = TextResponse(url, body=rr.text, encoding='utf-8')
                for el in tree.xpath("//table[@id='proxylisttable']/tbody/tr"):
                    try:
                        ip_addr = el.xpath(".//td[1]/text()").extract_first().strip()
                        port = el.xpath(".//td[2]/text()").extract_first().strip()
                        yield '{}:{}'.format(ip_addr, port)
                    except Exception as e1:
                        # logggg.error('freeProxyWall03 - {}'.format(e1.args))
                        pass

            except Exception as e:
                # logggg.error('freeProxyWall03 - {}'.format(e1.args))
                pass


if __name__ == '__main__':
    from CheckProxy import CheckProxy

    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyFirst)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxySecond)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyThird)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyFourth)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyFifth)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxySixth)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxySeventh)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyEight)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyNinth)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyTen)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyEleven)
    CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyTwelve)

    # CheckProxy.checkAllGetProxyFunc()

