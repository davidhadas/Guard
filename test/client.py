import requests
import random
import string

defaults = {
      "url": "sample-tests.sros-e621c7d733ece1fad737ff54a8912822-0000.us-south.containers.appdomain.cloud"
    , "scheme": "http"
    , "method": "GET"
    , "path": "/"
    , "data": ""
    , "queryKeys": 2
    , "queryVal": 2
    , "headersKeys": 2
    , "headersVal": 2
    , "cookiesKeys": 2
    , "cookiesVal": 2
    , "bodyKeys": 2
    , "bodyVal": 2
}


def send(param):
    url = param.get("url") or defaults["url"]
    method = param.get("method") or defaults["method"]
    scheme = param.get("scheme") or defaults["scheme"]
    path = param.get("path") or defaults["path"]

    queryKeys = param.get("queryKeys") or defaults["queryKeys"]
    queryVal = (param.get("queryVal") or defaults["queryVal"])*3
    headersKeys = param.get("headersKeys") or defaults["headersKeys"]
    headersVal = (param.get("headersVal") or defaults["headersVal"]) * 3
    cookiesKeys = param.get("cookiesKeys") or defaults["cookiesKeys"]
    cookiesVal = (param.get("cookiesVal") or defaults["cookiesVal"]) * 3
    bodyKeys = param.get("bodyKeys") or defaults["bodyKeys"]
    bodyVal = (param.get("bodyVal") or defaults["bodyVal"]) * 3

    data = param.get("data") or defaults["data"]

    query = {}
    for i in range(queryKeys):
        query["KEY-"+str(i)] = ''.join(random.choice(string.ascii_uppercase) for _ in range(random. randint(queryVal-1, queryVal+2)))
    headers = {}
    for i in range(headersKeys):
        headers["HEADER-"+str(i)] = ''.join(random.choice(string.ascii_uppercase) for _ in range(random.randint(headersVal - 1, headersVal + 2)))
    cookies = {}
    for i in range(cookiesKeys):
        cookies["COOKIE-" + str(i)] = ''.join(random.choice(string.ascii_uppercase) for _ in range(random.randint(cookiesVal - 1, cookiesVal + 2)))
    if not data:
        data = {}
        for i in range(bodyKeys):
            data["BODY-" + str(i)] = ''.join(random.choice(string.ascii_uppercase) for _ in range(random.randint(bodyVal - 1, bodyVal + 2)))

    print(method, scheme, query, headers, cookies, data)


    if (isinstance(data, dict)):
        res = requests.request(method, scheme+"://"+url+path, params=query, headers=headers, cookies=cookies, json=data)
    else:
        res = requests.request(method, scheme + "://" + url + path, params=query, headers=headers, cookies=cookies, data=data)

    print(res)

for i in range(1000):
    send({"queryKeys": 3})