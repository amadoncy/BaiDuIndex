#coding=gbk
from urllib.parse import quote, unquote, urlencode
import csv,datetime
import time
import requests
import pandas as pd
url1="https://index.baidu.com/api/SearchApi/region?region=0&word=长城雪茄&startDate=2023-03-1&endDate=2023-03-31"#地域分布数据
#region=932(地区编号）   通过修改region可查看各区的情况
url2="https://index.baidu.com/api/SocialApi/baseAttributes?wordlist[]=长城雪茄"   #人群属性（性别与年龄）画像数据TGI RATE
url3="https://index.baidu.com/api/SocialApi/interest?wordlist[]=长城雪茄&typeid="  #兴趣分布数据  typeid=代表兴趣名
CODE2PROVINCE = {
	"901":"山东","902":"贵州","903":"江西","904":"重庆","905":"内蒙古",
	"906":"湖北","907":"辽宁","908":"湖南","909":"福建","910":"上海",
	"911":"北京","912":"广西","913":"广东","914":"四川","915":"云南",
	"916":"江苏","917":"浙江","918":"青海","919":"宁夏","920":"河北",
	"921":"黑龙江","922":"吉林","923":"天津","924":"陕西","925":"甘肃",
	"926":"新疆","927":"河南","928":"安徽","929":"山西","930":"海南",
	"931":"台湾","932":"西藏","933":"香港","934":"澳门",
}   #区域代码
searchword="长城雪茄、王冠雪茄、狮牌雪茄、哈瓦那雪茄、库贝罗雪茄"  #搜索关键词列表
word = '王冠雪茄'#搜索关键词
encode_data = quote(word)#encode处理
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
start_time=datetime.date(2023,3,1)#开始爬取日期
nowdata=datetime.date.today()
print("下面将采集搜索关键词：{} 的数据".format(searchword))
print("*****  开始采集百度区域分布数据   *****")
while nowdata>=start_time:
    params = {
        'wordlist[]': str(word),
        'datelist': str(start_time.strftime('%Y%m%d'))  # 开始日期
    }
    print("| 正在读取搜索词：{}的数据......".format(word))
    res_index = requests.get(url1,headers=headers)
    #res_index.getCharacterEncoding()
    time.sleep(3)
    #print(res_index.text)
    json_index = res_index.json()
    #print(json_index)  # 辅助测试获取数据格式
    list_index = json_index['data']['region'][0]['prov']  # 关联词数据列表
    # 数据格式为{}
    #print(list_index)
    #构建excel格式数据[{},{},{}],每{}为一行数据
    dic_to_excl=[] #转换列表
    for k,v in list_index.items():
        dic={}    #临时生成字典保存每行数据
        dic["省份"]=CODE2PROVINCE[k]
        dic["访问数量"]=v
        dic_to_excl.append(dic)
    data = pd.DataFrame.from_dict(dic_to_excl)  # 将字典列表转pandas格式DF
    filename = "d:\\人群画像\\地区分布\\" + str(word) + start_time.strftime('%Y%m%d') + ".xlsx"
    print("| 正在写入文件{}............".format(filename))
    data.to_excel(filename, sheet_name="数量")  # 写入excel文件
    time.sleep(10)
    print("| 成功写入文件{}....... *".format(filename))
    start_time= start_time + datetime.timedelta(30)  # +一月
#print("已超过当前日期数据")

