#coding=gbk
from urllib.parse import quote, unquote, urlencode
import csv,datetime
import time
import requests
import pandas as pd
headers = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Connection': 'keep-alive',
    'Cookie':'BIDUPSID=7A9263F1A49465BFDFA73894842F53DD; PSTM=1675916815; BAIDUID=CA518EB72F7E5013A2FB7EB0DCFBCF73:FG=1; Hm_up_d101ea4d2a5c67dab98251f0b5de24dc={"uid_":{"value":"1938959305","scope":1}}; ZFY=YbOFCtjxvKzZRjPNGWXs5g8QgPJuY5dfC3ahmYUCVhM:C; BAIDUID_BFESS=CA518EB72F7E5013A2FB7EB0DCFBCF73:FG=1; BDUSS=ZVRTc5eTVuZFJQQjdIMHpCOUg1WVZETkphUW9GRXVtZFFLVDhiVFFHT21FMVprSVFBQUFBJCQAAAAAAAAAAAEAAADJK5JzAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKaGLmSmhi5kbl; bdindexid=nn5fvn9cm1um33m8g3af1a8m47; Hm_lvt_d101ea4d2a5c67dab98251f0b5de24dc=1680770719,1680772774,1680772962,1680774829; SIGNIN_UC=70a2711cf1d3d9b1a82d2f87d633bd8a04307872788XUIyBzoZbmoC0EUmy1h4wVVJSNKf5CNswHNST5z4LPNafOrtHghY0CTO01prK/cz9zIWjU7RzXXGA3/gULJMO6mhHJwrZ6J1g4IhTJ9capxkZSD7Rp1W9yM+d4Qv+6H+PXxEg5TwxnG7wPXD5tRDVq4Xtm/TQgLOE/rpFJ9QOLD/86oKZB/UbkUd3JyQg7IlGc/5msvTXKqF0SsVUj7LvmpmqiK/LW1VIfdtS7OKAKdvKjmGojBtFPxDCsJBYu3WacUwHtLQCM9VqlZuk6c7W2Zy089k4f8xAYNQcFY3C9o=37904906249876816380504582284069; __cas__rn__=430787278; __cas__st__212=2d52784b1e73de92a006c9f5a8c70ccc22ace5f04b486857bf01eaf7b0417cee82b7f225802919a46d1fa6b4; __cas__id__212=45843130; CPID_212=45843130; CPTK_212=158987234; Hm_lpvt_d101ea4d2a5c67dab98251f0b5de24dc=1680781433; BDUSS_BFESS=ZVRTc5eTVuZFJQQjdIMHpCOUg1WVZETkphUW9GRXVtZFFLVDhiVFFHT21FMVprSVFBQUFBJCQAAAAAAAAAAAEAAADJK5JzAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAKaGLmSmhi5kbl; __bid_n=186499d390aa4aa77e4207; FPTOKEN=a/hA0P3BHaTkpc1/0yCnKUai42nkrjo+9Ksot+fT6psbodhwoM6xzI29gME23C/KpRlbXdU5Kl0vQKvk2PP/x++ZBeVVgyWmQD6+2DsRldrrAusxlCA09pT1uhuobOZGm6ZddOAT2x98yu0x9Q5IAmhfTBRSE08Y+PAI4dEsSUawFwj810Tt7Fpgn+3eYame+wNJ1q1+QYSPQqlecTXWad97JeOsKv6SdD7JCvXWDg+FWDTsPWGWGU3x0Y7pc/MwVDVIOLg5v7eXwG9S+T4iXe+Km1smB5vcrGHapwK+0r0/EKtAG9ZABjiAaniYiCMfUnpWGdgpwiNvWAIrii/5Fh4aCdmV6JxWWvZIFoNwzSvLkmXRq0v2kwKfA5K4VO30F06I0srpDL3aRUHbD7kr1g==|CRSbl6i5TuLpDUtTPWO00jY6kjKmyuAMsN5QWSCjGbk=|10|0d58aca946cb07c0eab62eb03de17158; ab_sr=1.0.1_ZTY5NWRhY2RhMDU2YWFlMmU1MDZjYmFmYTkxZDJmNzhhYTM0YTAyYjYwZjUyOTk0YWU0NDI0YTNjZDAzMGY1NjFiNmFlN2YxYmYwODY2YTRkOTQ3Zjk5MDMxZjAwNTFjYjBlNjU5YWRhYzE3M2UyNDRhY2QwMGM3YTcyNDFkNzJmNDQ4ZGJjMzEyOTc2ZTkzZmYzZGVlMmVjYzBhZWQ4MzgyNTA0ZTI2MjkzYWQ2YjVmMzY2ZWUyMTJmMzMyMzYy; RT="z=1&dm=baidu.com&si=c82c1cc6-2d0c-45ae-bba2-312f7384bfa2&ss=lg51v99r&sl=0&tt=0&bcn=https://fclog.baidu.com/log/weirwood?type=perf&ld=3gq&ul=21x5g"',
    'Host': 'index.baidu.com',
    'Referer': 'https://index.baidu.com/v2/main/index.html',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="102", "Google Chrome";v="102"',
    'sec-ch-ua-mobile': '?0',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36'
}
searchword="长城雪茄、王冠雪茄、狮牌雪茄、哈瓦那雪茄、库贝罗雪茄"  #搜索关键词列表
words=searchword.split("、") #搜索关键词列表
print("下面将采集搜索关键词：{} 的数据".format(searchword))
print("*****  开始采集百度人群画像数据   *****")
for word in words: # 搜索关键词
    url2 = "https://index.baidu.com/api/SocialApi/baseAttributes?wordlist[]={}".format(word)  # 人群属性（性别与年龄）画像数据TGI RATE
    #encode_data = quote(word)  # encode处理
    print("| 正在读取:{}的人群画像数据.........".format(word))
    res_index = requests.get(url2,headers=headers)
    time.sleep(3)
    json_index = res_index.json()   #转json格式
    #print(json_index)  # 辅助测试获取数据格式
    if json_index['data']!="":
        list_index_gender = json_index['data']['result'][0]['gender']  # 男女比例数据
        list_index_age = json_index['data']['result'][0]['age']  # 年龄数据
        list_index_all = list_index_gender + list_index_age  # 合并数据
        #print(list_index_all)
        data_list = []  # 构建新的合并数据列表下，删除typid
        for dict_data in list_index_all:  # 删除typeid
            del dict_data["typeId"]
            data_list.append(dict_data)
        # print(data_list)
        # 数据格式为{}
        # print(list_index_gender)
        # print(list_index_age)
        # print(list_index_all)
        # 构建excel格式数据[{},{},{}],每{}为一行数据
        data_all = pd.DataFrame.from_dict(data_list)  # 将性别字典列表转pandas格式DF
        filename = "d:\\人群画像\\性别与年龄\\" + str(word) + "性别与年龄段分布" + ".xlsx"
        print("| 正在写入文件->{}............".format(filename))
        data_all.to_excel(filename, sheet_name="比例", index=False)  # 写入excel文件
        time.sleep(2)
        print("| 成功写入文件->{}..........  *".format(filename))
    else:
        print("！！！ 采集数据为空 ,检查搜索关键词是否正确 ")
print("* 数据采集完成 ！！！")

