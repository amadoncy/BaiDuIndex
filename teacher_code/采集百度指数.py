from selenium import webdriver
import datetime
import requests
import sys
import time
import json
import pandas as pd
import numpy as np
from requests.cookies import cookiejar_from_dict  #cook格式转换函数
from selenium.webdriver.common.by import By
import os
import pickle

#word_url = 'http://index.baidu.com/api/SearchApi/thumbnail?area=0&word={}'
auto_cook=[]  #获取cookies

# 添加cookies文件路径
COOKIES_FILE = "cookies.pkl"

def save_cookies(cookies):
    """保存cookies到文件"""
    try:
        with open(COOKIES_FILE, 'wb') as f:
            pickle.dump(cookies, f)
        print("Cookies已保存")
    except Exception as e:
        print(f"保存Cookies失败: {e}")

def load_cookies():
    """从文件加载cookies"""
    try:
        if os.path.exists(COOKIES_FILE):
            with open(COOKIES_FILE, 'rb') as f:
                cookies = pickle.load(f)
            print("已加载保存的Cookies")
            return cookies
    except Exception as e:
        print(f"加载Cookies失败: {e}")
    return None

def openbrowser():
    global browser
    top_list=[]
    # https://passport.baidu.com/v2/?loginhttps://index.baidu.com/v2/index.html#/
    url = "https://index.baidu.com/v2/index.html#/"  #百度指数网址
    # 打开谷歌浏览器
    browser = webdriver.Chrome()
    browser.get(url)
    browser.maximize_window()
    # time.sleep(10)
    # 找到id="TANGRAM__PSP_4__userName"的登录对话框
    browser.find_element(By.XPATH, '//*[@id="home"]/div[2]/div[1]/div[2]/div[1]/div[4]/span/span').click()
    time.sleep(2)
    uname=browser.find_element(By.XPATH, '//*[@id="TANGRAM__PSP_4__userName"]')
    upassword=browser.find_element(By.XPATH, '//*[@id="TANGRAM__PSP_4__password"]')
    ulogin = browser.find_element(By.XPATH, '//*[@id="TANGRAM__PSP_4__submit"]')
    account = [] #登录账号信息列表
    #获取账号和密码
    try:
        fileaccount = open("../resources/user_info.txt")
        accounts = fileaccount.readlines()
        for acc in accounts:
            account.append(acc.strip())
        fileaccount.close()
    except Exception as err:
        print(err)
        input("请正确在acount.txt里面写入账号密码")
        exit()
    #输入账号和密码
    uname.clear()
    uname.send_keys(account[0])
    time.sleep(3)
    upassword.clear()
    upassword.send_keys(account[1])
    time.sleep(3)
    ulogin.click()
    time.sleep(10)
    #获取cookie
    input("请输入回车继续")
    cookie=browser.get_cookies()
    print("COOKIES获取成功......")
    browser.quit()
    return cookie
def get_html(url, cookies=None):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        "Host": "index.baidu.com",
        "Referer": "http://index.baidu.com/v2/main/index.html",
        "Cipher-Text": "1652425237825_1652501356206_VBpwl9UG8Dvs2fAi91KToRTSAP7sDsQU5phHL97raPDFJdYz3fHf9hBAQrGGCs+qJoP7yb44Uvf91F7vqJLVL0tKnIWE+W3jXAI30xx340rhcwUDQZ162FPAe0a1jsCluJRmMLZtiIplubGMW/QoE/0Pw+2caH39Ok8IsudE4wGLBUdYg1/bKl4MGwLrJZ7H6wbhR0vT5X0OdCX4bMJE7vcwRCSGquRjam03pWDGZ51X15fOlO0qMZ2kqa3BmxwNlfEZ81l3L9nZdrc3/Tl4+mNpaLM7vA5WNEQhTBoDVZs6GBRcJc/FSjd6e4aFGAiCp1Y8MD66chTiykjIN51s7gbJ44JfVS0NjBnsvuF55bs="
    }
    
    # 如果没有传入cookies，使用默认的cookies
    if not cookies:
        print("警告：使用默认cookies，可能无法获取数据")
        cookies = [{'name': 'BAIDUID', 'value': '0B4A8F036F4CF170015C0E924974EEA6:FG=1', 'path': '/', 'domain': '.baidu.com', 'expiry': 1712327861, 'secure': False, 'httpOnly': False}, {'name': 'BDUSS', 'value': 'lFUmUxMHA3a2M1cmwwbkRCaGxaR1lrNnVYRDNqb1ozclBYbWdkYn5ZeEJabFprSVFBQUFBJCQAAAAAAAAAAAEAAADJK5JzAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEHZLmRB2S5kaF', 'path': '/', 'domain': '.baidu.com', 'expiry': 1939991873, 'secure': False, 'httpOnly': True}, {'name': 'SIGNIN_UC', 'value': '70a2711cf1d3d9b1a82d2f87d633bd8a04308043233mtO9gJzZZoIwQ4ciq4UN8o12035idqStHvvVNmVwX1DSI4SnPpzCJGbDK0BjS4%2F2Migh%2BwevtRXxiGGq2vr1zR9dAl4raxbmo83e0UNl5Io%2BpeMdDQUAzg46%2FFlw6VCekKjoJtYGkJWg03ZDjYjnHUGPEUxORxHj1x%2FSQDfTWw1lRUueX7aovAWMeO0ZjT1%2Fd7vbUmF%2BIf0F3HT%2BP065ygIuuoNhWQo%2FQ6y0tY4IWoEHH0FMmX%2FQOyEFQ%2B%2FKvNu3suu8DPz9%2FD2VOr5V%2Fl6fXjy78DXj9vx6JTQQfBRlJwk%3D77616278220480916128792678627622', 'path': '/', 'domain': '.baidu.com', 'expiry': 9223372036854776000, 'secure': False, 'httpOnly': True}, {'name': '__cas__rn__', 'value': '430804323', 'path': '/', 'domain': '.index.baidu.com', 'expiry': 9223372036854776000, 'secure': False, 'httpOnly': True}]

    # 获取cookies中的name和value,转化成requests可以使用的形式
    cook = {}  #格式转换后存放结果
    for ck in cookies:
        cook[ck['name']] = ck['value']
    
    # 发起requests请求时进行一步转换
    cookies = cookiejar_from_dict(cook)   #最终转换结果
    
    try:
        #开始requests请求
        response = requests.get(url, headers=headers, cookies=cookies)
        response.raise_for_status()  # 检查HTTP错误
        time.sleep(3)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {e}")
        print(f"URL: {url}")
        print(f"Headers: {headers}")
        print(f"Cookies: {cookies}")
        return None

def decrypt(t, e):
    '''
    数据解码函数
    '''
    try:
        if not t or not e:
            print("解密参数为空")
            return None
            
        n = list(t)
        i = list(e)
        a = {}
        result = []
        ln = int(len(n) / 2)
        start = n[ln:]
        end = n[:ln]
        for j, k in zip(start, end):
            a.update({k: j})
        for j in e:
            result.append(a.get(j))
        return ''.join(result)
    except Exception as e:
        print(f"解密过程出错: {e}")
        print(f"t: {t}")
        print(f"e: {e}")
        return None

def get_ptbk(uniqid, cookies=None):
    '''
    uniqid:获取爬取数据中用于加密的uniqid值
    '''
    url = 'http://index.baidu.com/Interface/ptbk?uniqid={}'
    resp = get_html(url.format(uniqid), cookies)
    if resp:
        try:
            data = json.loads(resp)
            if data.get('status') == 0 and 'data' in data:
                return data['data']
            else:
                print(f"获取ptbk失败: {data}")
        except json.JSONDecodeError as e:
            print(f"解析ptbk响应失败: {e}")
            print(f"响应内容: {resp}")
    return None

def get_data(keyword,area,start_date,end_date):
    '''
    keyword:搜索关键词
    area:地区编号
    start:开始日期
    end:结束日期
    '''
    # 尝试加载保存的cookies
    cookies = load_cookies()
    
    # 如果没有保存的cookies或cookies无效，则重新登录
    if not cookies:
        print("需要重新登录...")
        cookies = openbrowser()
        if cookies:
            save_cookies(cookies)
        else:
            print("登录失败，请检查用户名和密码是否正确")
            return None

    url = "https://index.baidu.com/api/SearchApi/index?area={}&word=[[%7B%22name%22:%22{}%22,%22wordType%22:1%7D]]&startDate={}&endDate={}".format(
        area,keyword, start_date,end_date)   #构建搜索带参数的url,area=97  代表成都地区
    print(start_date,end_date)
    response_text = get_html(url, cookies)
    
    try:
        # 解析JSON响应
        data = json.loads(response_text)
        
        if data['status'] != 0:
            print(f"获取数据失败: {data}")
            # 如果是因为登录状态失效，删除cookies文件并重试
            if data.get('message') == 'not login':
                print("登录状态已失效，需要重新登录")
                if os.path.exists(COOKIES_FILE):
                    os.remove(COOKIES_FILE)
                return get_data(keyword, area, start_date, end_date)
            return None
            
        # 检查数据结构
        if 'data' not in data:
            print(f"API返回数据格式错误: {data}")
            return None
            
        if 'uniqid' not in data['data']:
            print(f"API返回数据缺少uniqid: {data}")
            return None
            
        if 'userIndexes' not in data['data'] or not data['data']['userIndexes']:
            print(f"API返回数据缺少userIndexes: {data}")
            return None
            
        if 'all' not in data['data']['userIndexes'][0]:
            print(f"API返回数据缺少all字段: {data}")
            return None
            
        uniqid = data['data']['uniqid']    #获得uniqid值，用于解码
        encrypted_data = data['data']['userIndexes'][0]['all']['data']   #获取爬取的指数数据
        
        if not encrypted_data:
            print("未获取到指数数据")
            return None
            
        ptbk = get_ptbk(uniqid, cookies)            #调用get_ptbk(),获得最终的ptbk
        if not ptbk:
            print("获取解密密钥失败")
            return None
            
        result = decrypt(ptbk, encrypted_data)       #调用decrypt(),实现解码
        if not result:
            print("数据解密失败")
            return None
            
        result = result.split(',')
        
        start = start_date.split("-")   #分割日期字符串
        end = end_date.split("-")
        a = datetime.date(int(start[0]), int(start[1]), int(start[2]))  #构造日期
        b = datetime.date(int(end[0]), int(end[1]), int(end[2]))
        node = 0
        sheet_data =[]   #构建表格数据，便于转换成df
        
        for i in range(a.toordinal(), b.toordinal()):   #开始日期对于天数--结束日期对应天数
            ydict = {}   #得到{日期：date,指数：result[node]}
            date = datetime.date.fromordinal(i)  #通过天数计算出日期值
            ydict["日期"]=date
            ydict["指数"]=result[node]
            ydict["地区"]=searchareas[area]
            sheet_data.append(ydict)
            node += 1
            
        data=pd.DataFrame.from_dict(sheet_data)  # 将字典列表转DF数据格式
        print("正在采集百度指数.......")
        filename=keyword+searchareas[area]+start_date+"-"+end_date+".xlsx"  #构造文件名称
        data.to_excel("E:\\BaiDuIndex\\data\\"+filename,sheet_name = "数量",index=False)
        print("正在写入数据表->{}.....".format(filename))
        return None
        
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
        print(f"响应内容: {response_text}")
        return None
    except Exception as e:
        print(f"处理数据时出错: {e}")
        print(f"响应内容: {response_text}")
        return None
if __name__ == '__main__':
    searchkeywords =["长城雪茄","王冠雪茄","狮牌雪茄","哈瓦那雪茄","雪茄"] #预置搜索关键词
    searchareas = {514:"北京",57:"上海",94:"深圳",95:"广州",97:"成都",189:"合肥"}   #  北京、上海、广州、合肥、深圳和成都
    #采集2011年1月1日至2023年3月18日
    #s_date = ["2011-01-01","2012-01-01","2013-01-01","2014-01-01","2015-01-01","2016-01-01" "2017-01-01","2018-01-01","2019-01-01","2020-01-01","2021-01-01","2022-01-01","2023-01-01",]      #预置搜索开始日期

    #e_date =["2012-01-01","2013-01-01","2014-01-01","2015-01-01","2016-01-01" "2017-01-01","2018-01-01","2019-01-01","2020-01-01","2021-01-01","2022-01-01","2023-03-08"]          #预置搜索结束日期
    s_date = ["2023-01-01"]  # 预置搜索开始日期
    e_date = ["2023-04-30"]
    #auto_cook=openbrowser()     自动获取cookies
    ycount=len(s_date)
    for keyword in searchkeywords:
        for search_area in searchareas:
            for y_n in range(ycount):
                print("正在搜索:{}地区，{}年，{}的百度指数数据.....".format(searchareas[search_area],s_date[y_n], keyword))
                get_data(keyword, search_area, s_date[y_n], e_date[y_n])
                print("数据成功保存到文件")
                time.sleep(1)
    print("指数采集完成")
