import time
from selenium import webdriver
from utils.db_utils import DatabaseConnection
from utils.get_index_cookie_utils import get_index_cookie, get_login_user_info
from datetime import datetime, date
import pandas as pd
import requests
import json
import random
import urllib3
import os
import pickle
from selenium.webdriver.common.by import By
from requests.utils import cookiejar_from_dict
from config.city_codes import get_all_regions, get_region_provinces, get_province_code, get_city_code, get_province_cities
import logging
import gc


# 禁用SSL警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 添加cookies文件路径
COOKIES_FILE = "cookies.pkl"


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


def openbrowser():
    """通过浏览器获取新的cookies"""
    url = "https://index.baidu.com/v2/index.html#/"
    browser = webdriver.Chrome()
    try:
        browser.get(url)
        browser.maximize_window()
        
        # 点击登录按钮
        browser.find_element(By.XPATH, '//*[@id="home"]/div[2]/div[1]/div[2]/div[1]/div[4]/span/span').click()
        time.sleep(2)
        
        # 获取登录表单元素
        uname = browser.find_element(By.XPATH, '//*[@id="TANGRAM__PSP_4__userName"]')
        upassword = browser.find_element(By.XPATH, '//*[@id="TANGRAM__PSP_4__password"]')
        ulogin = browser.find_element(By.XPATH, '//*[@id="TANGRAM__PSP_4__submit"]')
        
        # 读取账号信息
        try:
            with open("../resources/user_info.txt") as f:
                account = [line.strip() for line in f.readlines()]
        except Exception as e:
            print(f"读取账号信息失败: {e}")
            return None
            
        # 输入账号密码
        uname.clear()
        uname.send_keys(account[0])
        time.sleep(3)
        upassword.clear()
        upassword.send_keys(account[1])
        time.sleep(3)
        ulogin.click()
        time.sleep(10)
        
        # 等待用户手动验证
        input("请完成登录验证后按回车继续...")
        
        # 获取cookies
        cookies = browser.get_cookies()
        print("成功获取新的Cookies")
        return cookies
        
    except Exception as e:
        print(f"浏览器操作失败: {e}")
        return None
    finally:
        browser.quit()


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
    保存数据到Excel文件，使用更保守的内存管理
    :param data: 数据列表
    :param keyword: 关键词
    """
    try:
        # 从数据中获取地区名称
        area_name = data[0]["地区"] if data and "地区" in data[0] else "全国"
        
        # 创建文件名（地名+关键词+采集时间）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{area_name}_{keyword}_{timestamp}.xlsx"
        filepath = os.path.join("./data/trend", filename)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # 直接转换为DataFrame并保存，避免分批处理
        df = pd.DataFrame(data)
        df.to_excel(filepath, index=False)
        
        print(f"数据已保存到Excel文件: {filename}")
        
        # 立即清理DataFrame
        del df
        gc.collect()
        
        return True
        
    except Exception as e:
        print(f"保存Excel文件失败: {e}")
        return False
    finally:
        # 确保清理所有临时对象
        if 'df' in locals():
            del df


def select_area(region=None, province=None, city=None):
    """选择地区
    Args:
        region: 区域名称（如：华东、华北等）
        province: 省份名称
        city: 城市名称（可选）
    Returns:
        tuple: (area_code, area_name) 地区代码和地区名称
    """
    try:
        # 如果没有提供任何参数，返回全国
        if not region:
            return 0, "全国"
            
        # 获取省份列表
        provinces = get_region_provinces(region)
        if not provinces or not province or province not in provinces:
            logging.error(f"无效的省份选择: region={region}, province={province}")
            return 0, "全国"
            
        # 如果没有指定城市，返回省份代码
        if not city:
            try:
                # 获取省份代码
                db = DatabaseConnection()
                try:
                    code = db.get_area_code(region=region, province=province)
                    if code is not None:  # 直接使用返回的代码
                        return code, province
                finally:
                    db.close()
                
                # 如果数据库查询失败，尝试使用配置文件中的代码
                province_code = get_province_code(province)
                if province_code:
                    return province_code, province
                
                logging.error(f"无法获取省份代码: {province}")
                return 0, "全国"
            except Exception as e:
                logging.error(f"获取省份代码失败: {str(e)}")
                return 0, "全国"
            
        # 如果指定了城市，获取城市代码
        cities = get_province_cities(province)
        if not cities or city not in cities:
            logging.error(f"无效的城市选择: province={province}, city={city}")
            return 0, "全国"
            
        try:
            # 获取城市代码
            db = DatabaseConnection()
            try:
                code = db.get_area_code(region=region, province=province, city=city)
                if code is not None:  # 直接使用返回的代码
                    return code, f"{province}{city}"
            finally:
                db.close()
            
            # 如果数据库查询失败，尝试使用配置文件中的代码
            city_code = get_city_code(province, city)
            if city_code:
                return city_code, f"{province}{city}"
            
            logging.error(f"无法获取城市代码: {province}{city}")
            return 0, "全国"
        except Exception as e:
            logging.error(f"获取城市代码失败: {str(e)}")
            return 0, "全国"

    except Exception as e:
        logging.error(f"选择地区失败: {str(e)}")
        return 0, "全国"  # 发生错误时默认返回全国


def get_last_record(db_cursor, keyword, area):
    """
    获取数据库中某个关键词和地区的最后一条记录
    """
    try:
        query = """
        SELECT date, index_value, area, keyword 
        FROM baidu_index_trends 
        WHERE keyword = %s AND area = %s 
        ORDER BY date DESC 
        LIMIT 1
        """
        db_cursor.execute(query, (keyword, area))
        return db_cursor.fetchone()
    except Exception as e:
        logging.error(f"获取最后一条记录失败: {e}")
        return None


def check_data_exists(db_cursor, date, keyword, area):
    """
    检查特定日期、关键词和地区的数据是否存在
    """
    try:
        query = """
        SELECT COUNT(*) 
        FROM baidu_index_trends 
        WHERE date = %s AND keyword = %s AND area = %s
        """
        db_cursor.execute(query, (date, keyword, area))
        count = db_cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        logging.error(f"检查数据存在失败: {e}")
        return False


def get_missing_dates(db_cursor, keyword, area):
    """
    获取数据库最后一条记录到今天之间缺失的日期
    """
    try:
        # 获取最后一条记录的日期
        query = """
        SELECT MAX(date) 
        FROM baidu_index_trends 
        WHERE keyword = %s AND area = %s
        """
        db_cursor.execute(query, (keyword, area))
        last_date = db_cursor.fetchone()[0]
        
        if not last_date:
            return None, None  # 数据库中没有记录
            
        # 计算到今天的日期差
        today = datetime.now().date()
        date_diff = (today - last_date).days
        
        if date_diff <= 0:
            return None, None  # 数据已是最新
            
        # 计算需要获取的日期范围
        start_date = last_date + pd.Timedelta(days=1)
        return start_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
        
    except Exception as e:
        logging.error(f"获取缺失日期失败: {e}")
        return None, None


def safe_float(val):
    try:
        if val is None or val == '' or str(val).lower() == 'nan':
            return None
        return float(val)
    except (ValueError, TypeError):
        return None


def save_data_to_db(data):
    """
    保存数据到数据库，包含数据比对和当天数据检查
    :param data: 数据列表，每个元素包含日期、指数、地区、关键词
    :return: (需要补充的开始日期, 结束日期) 或 (None, None)
    """
    db = None
    cursor = None
    try:
        db = DatabaseConnection()
        cursor = db.connection.cursor()
        
        # 创建表（如果不存在）
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS baidu_index_trends (
            id INT AUTO_INCREMENT PRIMARY KEY,
            date DATE NOT NULL,
            index_value INT NOT NULL,
            area VARCHAR(50) NOT NULL,
            keyword VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_trend (date, area, keyword)
        )
        """
        cursor.execute(create_table_sql)
        
        # 分批处理数据，每批100条
        batch_size = 100
        records_to_insert = []
        inserted_count = 0
        updated_count = 0
        
        for i in range(0, len(data), batch_size):
            batch = data[i:min(i + batch_size, len(data))]
            current_batch = []
            
            for item in batch:
                date_str = item["日期"].strftime("%Y-%m-%d")
                keyword = item["关键词"]
                area = item["地区"]
                index_value = safe_float(item["指数"])
                if index_value is None:
                    # 跳过或存为0
                    continue
                index_value = int(index_value)
                
                # 检查数据是否已存在
                cursor.execute("""
                    SELECT id, index_value FROM baidu_index_trends 
                    WHERE date = %s AND keyword = %s AND area = %s
                """, (date_str, keyword, area))
                
                existing = cursor.fetchone()
                if not existing:
                    # 不存在，插入新数据
                    current_batch.append((
                        date_str,
                        index_value,
                        area,
                        keyword
                    ))
                elif existing[1] != index_value:
                    # 存在但指数值不同，进行更新
                    cursor.execute("""
                        UPDATE baidu_index_trends 
                        SET index_value = %s, created_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (index_value, existing[0]))
                    updated_count += 1
            
            # 批量插入当前批次的新数据
            if current_batch:
                insert_sql = """
                INSERT INTO baidu_index_trends (date, index_value, area, keyword)
                VALUES (%s, %s, %s, %s)
                """
                cursor.executemany(insert_sql, current_batch)
                db.connection.commit()
                inserted_count += len(current_batch)
                
                # 清理当前批次
                current_batch.clear()
                gc.collect()
        
        if inserted_count > 0 or updated_count > 0:
            print(f"成功插入 {inserted_count} 条新数据，更新 {updated_count} 条已有数据")
        
        # 检查是否需要补充数据
        if data:
            missing_start, missing_end = get_missing_dates(cursor, data[0]["关键词"], data[0]["地区"])
            return missing_start, missing_end
        
        return None, None
        
    except Exception as e:
        print(f"保存数据到数据库失败: {e}")
        if db and db.connection:
            try:
                db.connection.rollback()
            except Exception as rollback_e:
                print(f"回滚事务失败: {rollback_e}")
        return None, None
        
    finally:
        # 分别关闭cursor和数据库连接
        if cursor:
            try:
                cursor.close()
            except Exception as e:
                print(f"关闭cursor失败: {e}")
        
        if db:
            try:
                db.close()
            except Exception as e:
                print(f"关闭数据库连接失败: {e}")
        
        # 清理局部变量
        if 'current_batch' in locals():
            del current_batch
        if 'records_to_insert' in locals():
            del records_to_insert
        gc.collect()


def process_batch_data(start_date_obj, points_per_day, result_data, keyword, area_name, batch_size=100):
    """
    分批处理数据以避免内存问题
    """
    processed_data = []
    total_points = len(result_data)
    
    for i in range(0, total_points, batch_size):
        batch = result_data[i:i + batch_size]
        for j, value in enumerate(batch):
            idx = i + j
            days_offset = int(idx / points_per_day)
            current_date = start_date_obj + pd.Timedelta(days=days_offset)
            processed_data.append({
                "日期": current_date,
                "指数": value,
                "地区": area_name,
                "关键词": keyword
            })
            
        # 及时清理不需要的对象
        if len(processed_data) >= batch_size * 2:
            yield processed_data
            processed_data = []
    
    if processed_data:
        yield processed_data


def get_trend_utils(username, keyword, area_code=0, area_name="全国", start_date=None, end_date=None):
    """
    一次性获取百度指数趋势数据
    :return: 趋势数据列表或None（如果发生错误）
    """
    try:
        # 设置日期范围
        if end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
        if start_date is None:
            start_date = (datetime.now() - pd.Timedelta(days=3650)).strftime('%Y-%m-%d')  # 10年数据
            
        logging.info(f"准备获取从 {start_date} 到 {end_date} 的数据")
        
        # 获取cookies
        cookies = load_cookies(username)
        if not cookies:
            logging.info("未找到有效cookies，尝试重新登录...")
            cookies = get_index_cookie(username)
            if cookies:
                save_cookies(cookies, username)
            else:
                logging.error("登录失败，请检查用户名和密码")
                return None
        
        # 构建API URL
        url = f"https://index.baidu.com/api/SearchApi/index?area={area_code}&word=[[%7B%22name%22:%22{keyword}%22,%22wordType%22:1%7D]]&startDate={start_date}&endDate={end_date}"
        
        # 获取数据
        response_text = get_html(url, cookies)
        if not response_text:
            logging.error("获取数据失败")
            return None
            
        data = json.loads(response_text)
        if data['status'] != 0:
            if data.get('message') == 'not login':
                db = DatabaseConnection()
                try:
                    db.delete_cookies(username)
                finally:
                    db.close()
            logging.error(f"API返回错误: {data.get('message', '未知错误')}")
            return None
            
        # 获取加密数据和uniqid
        encrypted_data = data['data']['userIndexes'][0]['all']['data']
        uniqid = data['data']['uniqid']
        if not encrypted_data:
            logging.error("未获取到加密数据")
            return None
        
        # 获取解密密钥
        ptbk = get_ptbk(uniqid, cookies)
        if not ptbk:
            logging.error("获取解密密钥失败")
            return None
        
        # 解密数据
        result = decrypt(ptbk, encrypted_data)
        if not result:
            logging.error("数据解密失败")
            return None
            
        # 处理数据
        result_data = result.split(',')
        start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date_obj = datetime.strptime(end_date, '%Y-%m-%d').date()
        total_days = (end_date_obj - start_date_obj).days + 1
        # 计算每个数据点的日期（假设数据点均匀分布）
        points_per_day = len(result_data) / total_days if total_days > 0 else 1
        data_dates = []
        for i in range(len(result_data)):
            days_offset = int(i / points_per_day)
            current_date = start_date_obj + pd.Timedelta(days=days_offset)
            if current_date > end_date_obj:
                break
            data_dates.append(current_date)
        # 只保留有数据的日期
        all_data = []
        for d, v in zip(data_dates, result_data):
            if v and v != '0':
                all_data.append({
                    "日期": d,
                    "指数": v,
                    "地区": area_name,
                    "关键词": keyword
                })
        # 保存数据
        if save_data_to_excel(all_data, keyword):
            save_data_to_db(all_data)
        return all_data

    except Exception as e:
        logging.error(f"获取趋势数据失败: {str(e)}")
        return None

    finally:
        gc.collect()
        # 强制清理内存
        import sys
        if hasattr(sys, 'exc_clear'):
            sys.exc_clear()


# 测试代码
if __name__ == "__main__":
    try:
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # 获取用户名
        username, _ = get_login_user_info()
        if not username:
            logging.error("获取用户信息失败")
            exit(1)

        # 获取趋势数据
        trend_data = get_trend_utils(username)
        if trend_data:
            logging.info("成功获取趋势数据")
        else:
            logging.error("获取趋势数据失败")
            
    except Exception as e:
        logging.error(f"程序执行出错: {str(e)}")
        import traceback
        logging.error(f"错误堆栈: {traceback.format_exc()}")
        
    finally:
        # 强制垃圾回收
        gc.collect()
        
        # 确保程序正常退出
        logging.info("程序执行完成") 