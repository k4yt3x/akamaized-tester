#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Name: Akamaized Tester
Forked From: Miyouzi
Date Created: July 19, 2019

Editor: K4YT3X
Last Modified: August 3, 2020
"""

# built-in imports
import argparse
import pathlib
import sys
import traceback

# third-party imports
from avalon_framework import Avalon
from global_dns import GlobalDNS
from pythonping import ping

VERSION = "5.0.0"


def parse_arguments():
    """ parse CLI arguments
    """
    parser = argparse.ArgumentParser(
        prog="akamaized_tester", formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "--host", help="hostname to test", default="upos-hz-mirrorakam.akamaized.net",
    )

    parser.add_argument(
        "--ip_list",
        type=pathlib.Path,
        help="specify resolved list of IP addresses",
        default="ip_list.txt",
    )

    return parser.parse_args()


def get_ip_ping_delay(ip):
    ping_result = ping(ip, count=5)
    average_delay = ping_result.rtt_avg_ms

    if average_delay < 100:
        Avalon.info(f"{ip}\t平均延迟: {average_delay} ms")

    else:
        Avalon.error(f"{ip}\t平均延迟: {average_delay} ms")

    return average_delay


args = parse_arguments()


try:
    resolved_ip_list = GlobalDNS(args.host)
    Avalon.info("第一次解析:")
    ip_list = resolved_ip_list.get_ip_list()

    Avalon.info("第二次解析:")
    resolved_ip_list.resolve()
    ip_list = ip_list | resolved_ip_list.get_ip_list()

    Avalon.info("第三次解析:")
    resolved_ip_list.resolve()
    ip_list = ip_list | resolved_ip_list.get_ip_list()

except BaseException:
    Avalon.error("进行全球解析时遇到未知错误: ")
    traceback.print_exc()

    if args.ip_list.is_file():
        Avalon.info("将读取本地保存的ip列表")
        with args.ip_list.open("r", encoding="utf-8") as ip_list_file:
            ip_list = ip_list_file.read().splitlines()

    else:
        Avalon.error("没有本地保存的ip列表！程序终止！")
        sys.exit(1)


Avalon.info(f"共取得 {len(ip_list)} 个 IP, 开始测试延迟")

ip_info = []
low_latency_ips = []

for ip in ip_list:
    delay = get_ip_ping_delay(ip)
    ip_info.append({"ip": ip, "delay": delay})

    if delay < 100:
        low_latency_ips.append({"ip": ip, "delay": delay})


if len(low_latency_ips) > 0:
    Avalon.info("基于当前网络环境, 以下为延迟低于 100 ms 的IP")
    low_latency_ips.sort(key=lambda k: k["delay"])

    for ip in low_latency_ips:
        Avalon.info(f"{ip['ip']}\t平均延迟: {ip['delay']} ms")

else:
    ip_info.sort(key=lambda k: k["delay"])
    Avalon.info("本次测试未能找到延迟低于 100 ms 的 IP! 以下为延迟最低的 3 个节点")
    for i in range(0, 3):
        Avalon.info(f"{ip_info[i]['ip']}\t平均延迟: {ip_info[i]['delay']} ms")
