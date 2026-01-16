"""
@Time ： 2026/1/15
@Auth ： CST21052
@File ：test_login.py
@IDE ：PyCharm
@Motto：Do one thing at a time, and do well.
@requirement:
"""
import requests
url = "http://127.0.0.1:8000/api/token/"
data = {
    "username":"yyp",
    "password":"yyp123456"
}
try:
    response = requests.post(url, data=data)
    print(response.json())
    print(response.status_code)
except Exception as e:
    print(e)