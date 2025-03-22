from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import logging
from db_utils import DatabaseConnection

url = 'https://index.baidu.com/v2/index.html#/'
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 Edg/133.0.0.0',
    'accept': '*/*',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'max-age=0',
    'dnt': '1'
}

def get_login_user_info():
    """获取登录信息"""
    try:
        with open('../resources/user_info.txt', 'r', encoding='utf-8') as f:
            username = f.readline().strip()
            password = f.readline().strip()
        return username, password
    except Exception as e:
        logging.error(f"读取用户信息失败: {str(e)}")
        return None, None

def get_index_cookie(username, password):
    """获取百度指数的cookies并保存到数据库"""
    try:
        # 配置无头模式
        chrome_options = Options()
        chrome_options.add_argument(f'--user-agent={headers["user-agent"]}')
        driver = webdriver.Chrome(options=chrome_options)
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

        input('请扫码登录、或者手机号验证登录,输入回车确认')

        # 验证登录状态
        username_login = driver.find_element(By.XPATH, '//*[@id="home"]/div[2]/div[1]/div[2]/div[1]/div[4]/span/span').text
        if username_login is not None:
            # 获取cookies
            cookies = driver.get_cookies()
            cookies_dict = {cookie['name']: cookie['value'] for cookie in cookies}
            
            # 保存cookies到数据库
            db = DatabaseConnection()
            if db.save_cookies(username, cookies_dict):
                logging.info("Cookies 获取并保存成功")
                return cookies_dict
            else:
                logging.error("保存Cookies到数据库失败")
                return None
        else:
            logging.error("登录失败")
            return None

    except Exception as e:
        logging.error(f"获取Cookies失败: {str(e)}")
        return None
    finally:
        driver.quit()

def get_cookie():
    """主函数"""
    # 设置日志
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    username, password = get_login_user_info()
    if username and password:
        cookies = get_index_cookie(username, password)
        if cookies:
            print("Cookies 获取成功")
        else:
            print("Cookies 获取失败")
    else:
        print("获取用户信息失败")

if __name__ == "__main__":
    get_cookie()
