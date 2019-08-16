# import requests
#
# url = 'http://192.168.50.144:8000'
# res = requests.get(url)
# proxy = None
# if res.status_code == 200:
#     proxy = res.text
#
# proxies= {
#     'http': 'sdg_develop:sdg666888@%s' % (proxy),
#     'https': 'sdg_develop:sdg666888@%s' % (proxy)
# }
#
# res = requests.get('https://www.baidu.com', proxies=proxies)
# print(res.text)


import requests

url = "https://pagoda-buy-acc.pagoda.com.cn:11521/api/v1/category/goods/-1/1/2/13"

querystring = {"_appInfo[channel]":"AppStore","_appInfo[deviceID]":"device2495146","_appInfo[model]":"iPhone 6s Plus","_appInfo[os]":"iOS 10.3.3","_appInfo[verCode]":"3.3.2","_appInfo[verName]":"3.3.2.0","_appInfo%5BverName%5D":"3.3.2.0","_appInfo%5BverCode%5D":"3.3.2","_appInfo%5Bos%5D":"iOS%2010.3.3","_appInfo%5Bmodel%5D":"iPhone%206s%20Plus","_appInfo%5BdeviceID%5D":"device2495146","_appInfo%5Bchannel%5D":"AppStore"}

headers = {
    'Host': "pagoda-buy-acc.pagoda.com.cn:11521",
    'userToken': "",
    'cityID': "1",
    'X-DEFINED-appinfo': '''{"deviceID":"device2495146","os":"iOS 10.3.3","verCode":"3.3.2","model":"iPhone 6s Plus","channel":"AppStore","verName":"3.3.2.0"}''',
    'Accept': "*/*",
    'User-Agent': "PagodaBuy/3.3.2 (iPhone; iOS 10.3.3; Scale/3.00)",
    'Accept-Language': "zh-Hans-CN;q=1, zh-Hant-CN;q=0.9",
    'Accept-Encoding': "gzip, deflate",
    'Connection': "keep-alive",
    'Cache-Control': "no-cache",
    'Postman-Token': "1220d170-85f5-4c63-91e8-cf294762c722,d2927903-2d6a-485b-bfa7-faad40bcce90",
    'cache-control': "no-cache"
    }

response = requests.request("GET", url, headers=headers, params=querystring, verify=False)

print(response.text)