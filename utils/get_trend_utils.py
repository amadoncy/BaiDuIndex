import time
from db_utils import DatabaseConnection
from get_index_cookie_utils import get_index_cookie, get_login_user_info
from datetime import datetime, date
import pandas as pd
import requests
import json
import random
import urllib3
from requests.utils import cookiejar_from_dict


# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def save_cookies(cookies, username):
    """保存cookies到数据库"""
    try:
        db = DatabaseConnection()
        db.save_cookies(username, cookies)
        print("Cookies已保存到数据库")
    except Exception as e:
        print(f"保存Cookies失败: {e}")


def load_cookies(username):
    """从数据库加载cookies"""
    try:
        db = DatabaseConnection()
        cookies = db.get_cookies(username)
        if cookies:
            print("已从数据库加载Cookies")
            return cookies
    except Exception as e:
        print(f"加载Cookies失败: {e}")
    return None


def get_random_headers():
    """
    生成随机请求头
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
        "Host": "index.baidu.com",
        "Referer": "http://index.baidu.com/v2/main/index.html",
        "Accept": "application/json, text/plain, */*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Sec-Ch-Ua": '"Not A(Brand";v="99", "Google Chrome";v="89", "Chromium";v="89"',
        "Sec-Ch-Ua-Mobile": "?0",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin"
    }
    return headers


def get_html(url, cookies=None, retry_count=3):
    """
    发送HTTP请求获取数据，带重试机制
    :param url: 请求URL
    :param cookies: cookies字典
    :param retry_count: 重试次数
    :return: 响应内容
    """
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

    # 处理cookies格式
    if isinstance(cookies, dict):
        # 如果cookies已经是字典格式，直接使用
        cook = cookies
    else:
        # 如果是列表格式，转换为字典
        cook = {}
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
    """
    数据解码函数
    :param t: 解密密钥
    :param e: 加密数据
    :return: 解密后的数据
    """
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
    """
    获取解密密钥
    :param uniqid: 唯一ID
    :param cookies: cookies字典
    :return: 解密密钥
    """
    url = f'http://index.baidu.com/Interface/ptbk?uniqid={uniqid}'
    resp = get_html(url, cookies)
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


def save_data_to_excel(data, keyword):
    """
    保存数据到Excel文件
    :param data: 数据列表
    :param keyword: 关键词
    """
    # 创建DataFrame
    df = pd.DataFrame(data)

    # 创建文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{keyword}_{timestamp}.xlsx"

    # 保存到Excel
    df.to_excel("E:\\BaiDuIndex\\data\\"+filename, index=False)
    print(f"数据已保存到Excel文件: {filename}")
    return filename


def get_trend_utils(username):
    """
    获取百度指数趋势数据
    :param username: 用户名
    :return: 趋势数据
    """
    # 尝试从数据库加载cookies
    cookies = load_cookies(username)
    # 如果没有保存的cookies或cookies无效，则重新登录
    if not cookies:
        print("需要重新登录...")
        username, password = get_login_user_info()
        if not username or not password:
            print("获取用户信息失败")
            return None
        cookies = get_index_cookie(username, password)
        if cookies:
            save_cookies(cookies, username)
        else:
            print("登录失败，请检查用户名和密码是否正确")
            return None

    word = input("请输入要查询的关键词: ")

    try:
        # 设置日期范围（默认最近30天）
        end_date = datetime.now().strftime('%Y-%m-%d')
        start_date = (datetime.now() - pd.Timedelta(days=3600)).strftime('%Y-%m-%d')

        # 设置地区（默认全国）
        area = 0

        # 构建API URL
        url = f"https://index.baidu.com/api/SearchApi/index?area={area}&word=[[%7B%22name%22:%22{word}%22,%22wordType%22:1%7D]]&startDate={start_date}&endDate={end_date}"
        print("请求URL:", url)  # 调试信息

        # 获取数据
        print("正在获取数据...")
        response_text = get_html(url, cookies)
        if not response_text:
            print("获取数据失败，响应为空")
            return None

        try:
            data = json.loads(response_text)

            if data['status'] != 0:
                print(f"获取数据失败: {data}")
                # 如果是因为登录状态失效，删除数据库中的cookies并重试
                if data.get('message') == 'not login':
                    print("登录状态已失效，需要重新登录")
                    db = DatabaseConnection()
                    db.delete_cookies(username)
                    return get_trend_utils(username)
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

            # 获取加密数据和uniqid
            encrypted_data = data['data']['userIndexes'][0]['all']['data']
            uniqid = data['data']['uniqid']


            if not encrypted_data:
                print("未获取到指数数据")
                return None

            # 等待一段时间
            time.sleep(random.uniform(2, 4))

            # 获取解密密钥
            print("正在解密数据...")
            ptbk = get_ptbk(uniqid, cookies)
            if not ptbk:
                print("获取解密密钥失败")
                return None

            # 解密数据
            result = decrypt(ptbk, encrypted_data)
            if not result:
                print("数据解密失败")
                return None

            result = result.split(',')

            # 获取实际的数据点数量
            data_points = len(result)
            print(f"获取到 {data_points} 个数据点")

            # 生成日期列表
            start = start_date.split("-")
            end = end_date.split("-")
            start_date = date(int(start[0]), int(start[1]), int(start[2]))
            end_date = date(int(end[0]), int(end[1]), int(end[2]))  # 使用 date 而不是 datetime.date

            # 计算日期间隔
            total_days = (end_date - start_date).days
            if total_days <= 0:
                print("日期范围无效")
                return None

            # 计算每天的数据点数量
            points_per_day = data_points / total_days

            # 构建数据
            sheet_data = []
            for i in range(data_points):
                ydict = {}
                # 根据数据点索引计算对应的日期
                days_offset = int(i / points_per_day)
                current_date = start_date + pd.Timedelta(days=days_offset)
                ydict["日期"] = current_date
                ydict["指数"] = result[i]
                ydict["地区"] = "全国"
                ydict["关键词"] = word
                sheet_data.append(ydict)

            # 转换为DataFrame
            data = pd.DataFrame.from_dict(sheet_data)

            if not data.empty:
                print(f"获取到 {len(data)} 个数据点")
                # 保存到Excel
                excel_file = save_data_to_excel(data.to_dict('records'), word)
                print(f"数据已保存到Excel文件: {excel_file}")
                return data.to_dict('records')
            else:
                print("获取图表数据失败")
                return None

        except json.JSONDecodeError as e:
            print(f"JSON解析错误: {e}")
            print(f"响应内容: {response_text}")
            return None

    except Exception as e:
        print(f"获取数据失败: {str(e)}")
        print("错误类型:", type(e))  # 调试信息
        import traceback
        print("错误堆栈:", traceback.format_exc())  # 调试信息
        return None


# 测试代码
if __name__ == "__main__":
    try:
        # 获取用户名
        username, _ = get_login_user_info()
        if not username:
            print("获取用户信息失败")
            exit(1)

        # 获取趋势数据
        trend_data = get_trend_utils(username)
        if trend_data:
            print("趋势数据:", trend_data)
        else:
            print("获取趋势数据失败")
    except Exception as e:
        print(f"测试过程中出错: {str(e)}")
