# 导入requests包
import requests
import json

url = "http://httpbin.org/post"
data = {"name": "plusroax", "age": 18}  # Post请求发送的数据，字典格式
res = requests.post(
    url=url, data=data
)  # 这里传入的data,是body里面的数据。params是拼接url时的参数

print("发送的body:", res.request.body)
print("response返回结果：", json.loads(res.text))
