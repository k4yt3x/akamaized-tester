#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: Akamaized Tester GlobalDNS Resolver
Forked From: Miyouzi
Date Created: July 19, 2019

Editor: K4YT3X
Last Modified: August 3, 2020
"""

# built-in imports
import re
import requests
import socket
import time

# third-party imports
from avalon_framework import Avalon
from bs4 import BeautifulSoup
import dns.resolver


class GlobalDNS:
    def __init__(self, domain: str, max_retries: int = 3):
        self._domain = domain
        self._max_retries = max_retries

        # initialize class variables
        self._ip_list = set([])
        self._dns_id = set([])
        self._session = requests.session()
        self._token = ""
        self._src = None

        # initialize other data
        self._init_header()
        self._session.headers.update(self._request_headers)

    def _init_header(self):
        # 伪装为Chrome
        self._request_headers = {
            "Host": "www.whatsmydns.net",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:69.0) Gecko/20100101 Firefox/69.0",
            # "referer": "https://" + host + "/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-TW,zh;q=0.8,zh-HK;q=0.6,en-US;q=0.4,en;q=0.2",
            # "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
            "TE": "Trailers",
        }

    def _request(self, url):
        error_cnt = 0
        while True:
            try:
                f = self._session.get(url, timeout=10)
                break
            except requests.exceptions.RequestException as e:
                # print('请求出现异常')
                if error_cnt >= self._max_retry:
                    raise e
                time.sleep(3)
                error_cnt += 1
        return BeautifulSoup(f.content, "lxml")

    def _get_src(self):
        bf4 = self._request(f"https://www.whatsmydns.net/#A/{self._domain}")
        # bf4 = self._request('https://www.whatsmydns.net/')
        self._src = bf4

    def _get_token(self):
        token = self._src.find("input", id="_token")
        self._token = token.get("value")

    def _get_dns_id(self):
        a = self._src.find_all("tr")
        for id in a:
            self._dns_id.add(id.get("data-id"))
        # print(self._dns_id)

    def _extend_query(self):
        # 本地解析
        A = dns.resolver.query(self._domain, "A")
        for i in A:
            self._ip_list.add(i.address)

        # 谷歌解析
        resolver = dns.resolver.Resolver()
        resolver.nameservers = [socket.gethostbyname("8.8.4.4")]
        A = resolver.query(self._domain, "A")
        for i in A:
            self._ip_list.add(i.address)

        # 腾讯解析
        resolver.nameservers = [socket.gethostbyname("119.29.29.29")]
        A = resolver.query(self._domain, "A")
        for i in A:
            self._ip_list.add(i.address)

        # 阿里解析
        resolver.nameservers = [socket.gethostbyname("223.5.5.5")]
        A = resolver.query(self._domain, "A")
        for i in A:
            self._ip_list.add(i.address)

    def _global_query(self):
        for dns_id in self._dns_id:
            url = f"https://www.whatsmydns.net/api/check?server={dns_id}&type=A&query={self._domain}&_token={self._token}"

            try:
                page_source = self._request(url)
                ips = str(page_source.contents[0])
                ip = re.findall(r"\d+\.\d+\.\d+\.\d+", ips)
                self._ip_list = self._ip_list | set(ip)
            except IndexError:
                # 该 DNS 失效
                pass

    def get_ip_list(self):

        if len(self._ip_list) == 0:
            # 如果尚未解析
            self.resolve()
        return self._ip_list

    def resolve(self):
        Avalon.info(f"正在对 {self._domain} 进行全球解析……")
        self._session.cookies.clear()
        self._get_src()
        self._get_token()
        self._get_dns_id()
        self._global_query()
        self._extend_query()
        Avalon.info(f"{self._domain} 的全球解析已完成")
