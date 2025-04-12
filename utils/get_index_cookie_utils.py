from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import logging
import os
import time
import requests
from utils.db_utils import DatabaseConnection
import random

url = 'https://index.baidu.com/v2/index.html#/'
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0',
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'max-age=0',
    'dnt': '1'
}

def check_internet_connection():
    """检查网络连接"""
    try:
        # 尝试访问百度
        logging.info("正在检查网络连接...")
        response = requests.get('https://www.baidu.com', timeout=5)
        if response.status_code == 200:
            logging.info("网络连接正常")
            return True
        else:
            logging.error(f"网络连接异常，状态码：{response.status_code}")
            return False
    except requests.RequestException as e:
        logging.error(f"网络连接失败：{str(e)}")
        return False

def wait_for_internet():
    """等待网络连接恢复"""
    retry_count = 0
    max_retries = 3
    while retry_count < max_retries:
        if check_internet_connection():
            return True
        retry_count += 1
        if retry_count < max_retries:
            logging.warning(f"第{retry_count}次网络连接失败，5秒后重试...")
            time.sleep(5)
    logging.error(f"网络连接失败，已重试{max_retries}次")
    return False

def get_login_user_info(cookie=None):
    """获取登录信息
    Args:
        cookie: 可选的cookie字符串，用于验证登录状态
    Returns:
        tuple: (username, password) 或 None
    """
    try:
        if cookie:
            # 如果提供了cookie，验证是否有效
            try:
                headers = generate_random_header()
                headers['Cookie'] = cookie if isinstance(cookie, str) else '; '.join([f"{k}={v}" for k, v in cookie.items()])
                response = requests.get('https://index.baidu.com/api/SugApi/sug?inputword=test', headers=headers)
                if response.status_code == 200 and response.json()['status'] == 0:
                    return True
            except:
                return False

        # 获取resources目录的绝对路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        resources_dir = os.path.join(os.path.dirname(current_dir), 'resources')
        
        # 确保resources目录存在
        if not os.path.exists(resources_dir):
            os.makedirs(resources_dir)
            
        user_info_path = os.path.join(resources_dir, 'user_info.txt')
        
        # 如果文件不存在，创建默认用户信息
        if not os.path.exists(user_info_path):
            with open(user_info_path, 'w', encoding='utf-8') as f:
                f.write('your_username\nyour_password')
            logging.info(f"已创建默认用户信息文件：{user_info_path}")
            logging.info("请修改文件内容为您的实际用户名和密码")
            return None, None
            
        # 读取用户信息
        with open(user_info_path, 'r', encoding='utf-8') as f:
            username = f.readline().strip()
            password = f.readline().strip()
            
        # 验证用户信息是否为默认值
        if username == 'your_username' or password == 'your_password':
            logging.error("请修改user_info.txt中的默认用户名和密码")
            return None, None
            
        return username, password
    except Exception as e:
        logging.error(f"读取用户信息失败: {str(e)}")
        return None, None

def get_index_cookie(username):
    """获取百度指数的cookies
    Args:
        username: 用户名
    Returns:
        str: cookie字符串或None
    """
    try:
        logging.info(f"开始获取用户 {username} 的cookies...")

        # 检查网络连接
        if not wait_for_internet():
            raise Exception("无法连接到网络，请检查网络设置")

        # 先从数据库获取cookies
        logging.info("尝试从数据库获取cookies...")
        db = DatabaseConnection()
        cookies = db.get_cookies(username)

        if cookies:
            logging.info("从数据库获取到cookies，验证是否有效...")
            # 验证cookies是否有效
            if get_login_user_info(cookies):
                logging.info("cookies验证有效")
                return cookies
            else:
                logging.info("cookies已失效，需要重新登录")

        # 如果没有有效的cookies，则重新登录获取
        logging.info("尝试获取登录信息...")
        username, password = get_login_user_info()
        if not username or not password:
            raise Exception("获取用户信息失败")

        # 配置Chrome选项
        chrome_options = Options()
        chrome_options.add_argument(f'--user-agent={headers["user-agent"]}')
        driver = webdriver.Chrome(options=chrome_options)
        
        try:
            driver.get(url)
            driver.implicitly_wait(5)
            driver.maximize_window()
            
            # 点击登录按钮
            driver.find_element(By.XPATH, '//*[@id="home"]/div[2]/div[1]/div[2]/div[1]/div[4]/span/span').click()
            
            # 输入用户名和密码
            driver.find_element(By.XPATH, '//*[@id="TANGRAM__PSP_4__userName"]').click()
            driver.find_element(By.XPATH, '//*[@id="TANGRAM__PSP_4__userName"]').send_keys(username)
            driver.find_element(By.XPATH, '//*[@id="TANGRAM__PSP_4__password"]').click()
            driver.find_element(By.XPATH, '//*[@id="TANGRAM__PSP_4__password"]').send_keys(password)
            
            # 点击登录
            driver.find_element(By.XPATH, '//*[@id="TANGRAM__PSP_4__submit"]').click()

            # 等待用户扫码或验证
            input('请扫码登录、或者手机号验证登录,输入回车确认')

            # 验证登录状态
            username_login = driver.find_element(By.XPATH, '//*[@id="home"]/div[2]/div[1]/div[2]/div[1]/div[4]/span/span').text
            if username_login is not None:
                # 获取cookies
                cookies = driver.get_cookies()
                cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}
                
                # 保存cookies到数据库
                if db.save_cookies(username, cookies_dict):
                    logging.info("Cookies 获取并保存成功")
                    return cookies_dict
                else:
                    raise Exception("保存Cookies到数据库失败")
            else:
                raise Exception("登录失败")

        finally:
            driver.quit()

    except Exception as e:
        logging.error(f"获取Cookies失败: {str(e)}")
        return None
    finally:
        if 'db' in locals():
            db.close()

def get_cookie():
    """主函数"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    username, password = get_login_user_info()
    if username and password:
        cookies = get_index_cookie(username)
        if cookies:
            print("Cookies 获取成功")
        else:
            print("Cookies 获取失败")
    else:
        print("获取用户信息失败")

def generate_random_header():
    """生成随机请求头"""
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edge/91.0.864.59',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'
    ]

    return {
        'user-agent': random.choice(user_agents),
        'accept': '*/*',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'cache-control': 'no-cache',
        'dnt': '1',
        'pragma': 'no-cache',
        'sec-ch-ua': '"Google Chrome";v="93", " Not;A Brand";v="99", "Chromium";v="93"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin'
    }

def get_trend_utils(username, keyword, area_code, area_name):
    """获取百度指数趋势数据
    Args:
        username: 用户名
        keyword: 搜索关键词
        area_code: 地区代码
        area_name: 地区名称
    Returns:
        dict: 包含趋势数据的字典
    """
    try:
        # 获取cookie
        cookie = get_index_cookie(username)
        if not cookie:
            raise Exception("获取cookie失败")

        # 构建请求URL
        url = f"https://index.baidu.com/api/SearchApi/index?area={area_code}&word=[[%7B%22name%22:%22{keyword}%22,%22wordType%22:1%7D]]"

        # 发送请求
        headers = generate_random_header()
        cookie_str = '; '.join([f"{k}={v}" for k, v in cookie.items()])
        headers['Cookie'] = cookie_str
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()

        if data['status'] != 0:
            raise Exception(f"获取数据失败：{data.get('message', '未知错误')}")

        # 解析数据
        result = {
            "关键词": keyword,
            "地区": area_name,
            "时间范围": f"{data['data']['userIndexes'][0]['startDate']} 至 {data['data']['userIndexes'][0]['endDate']}",
            "数据点数": len(data['data']['userIndexes'][0]['all']['data']),
            "指数统计": {
                "最大值": max(data['data']['userIndexes'][0]['all']['data']),
                "最小值": min(data['data']['userIndexes'][0]['all']['data']),
                "平均值": sum(data['data']['userIndexes'][0]['all']['data']) / len(data['data']['userIndexes'][0]['all']['data'])
            }
        }

        return result
    except Exception as e:
        logging.error(f"获取趋势数据失败: {str(e)}")
        raise

if __name__ == "__main__":
    get_cookie()
