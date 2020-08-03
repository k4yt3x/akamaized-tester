# Akamaized Tester

此程序从 miyouzi/akamTester fork 而来，诣在于解决一些代码和文档上的问题。

此程序被设计用来批量测试B站海外 CDN 节点延迟，找出最低延迟的节点。

当未指定域名时，该程序默认测试 `upos-hz-mirrorakam.akamaized.net`。

运行完程序找到延迟最低的 IP 之后，在 Hosts 中追加以下一行

```console
最低延迟的IP upos-hz-mirrorakam.akamaized.net
```

**在 Windows 7 上需要使用管理员权限运行**

## EXE 文件运行

不熟悉Python的用户从 [releases](https://github.com/k4yt3x/akamaized-tester/releases/latest) 下载exe文件直接使用。

## 源码运行

首先安装 Python 依赖文件

```shell
pip3 install -U -r requirements.txt
```

然后用 Python 运行主程序文件

```shell
python3 akamaized_tester.py
```

## 指定测试域名

可以用 `--host` 参数指定测试的域名

```shell
python3 akamaized_tester.py --host upos-sz-mirrorks3.bilivideo.com
```
