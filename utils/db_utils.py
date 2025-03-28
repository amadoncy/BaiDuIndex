import pymysql
import logging
from config.database import DB_CONFIG
import json
from datetime import datetime
import sqlite3
import os

# 配置日志
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s - %(message)s')

class DatabaseConnection:
    def __init__(self):
        self.connection = None
        self.connect()
        self.create_tables()

    def connect(self):
        """连接到数据库"""
        try:
            logging.debug("尝试连接数据库...")
            logging.debug(f"连接信息: host={DB_CONFIG['host']}, port={DB_CONFIG['port']}, user={DB_CONFIG['user']}, database={DB_CONFIG['db']}")
            
            self.connection = pymysql.connect(
                host=DB_CONFIG['host'],
                port=DB_CONFIG['port'],
                user=DB_CONFIG['user'],
                password=DB_CONFIG['password'],
                database=DB_CONFIG['db'],
                charset=DB_CONFIG['charset']
            )
            self.cursor = self.connection.cursor()
            logging.debug("数据库连接成功")
            return True
        except pymysql.Error as e:
            error_code = e.args[0]
            error_message = e.args[1] if len(e.args) > 1 else str(e)
            logging.error(f"数据库连接失败: [Error {error_code}] {error_message}")
            
            if error_code == 1045:  # 访问被拒绝
                logging.error("用户名或密码错误")
            elif error_code == 1049:  # 数据库不存在
                logging.error("数据库不存在")
                try:
                    # 尝试创建数据库
                    temp_conn = pymysql.connect(
                        host=DB_CONFIG['host'],
                        port=DB_CONFIG['port'],
                        user=DB_CONFIG['user'],
                        password=DB_CONFIG['password']
                    )
                    with temp_conn.cursor() as cursor:
                        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['db']}")
                    temp_conn.close()
                    logging.debug("成功创建数据库，正在重新连接...")
                    return self.connect()
                except Exception as create_error:
                    logging.error(f"创建数据库失败: {str(create_error)}")
            return False
        except Exception as e:
            logging.error(f"连接数据库时发生未知错误: {str(e)}")
            return False

    def create_tables(self):
        """创建必要的数据库表"""
        try:
            logging.info("开始创建数据库表...")
            with self.connection.cursor() as cursor:
                # 创建用户表
                logging.info("创建users表...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(50) NOT NULL UNIQUE,
                        password VARCHAR(255) NOT NULL,
                        phone VARCHAR(20) NOT NULL UNIQUE,
                        email VARCHAR(100) NOT NULL UNIQUE,
                        last_login TIMESTAMP NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                logging.info("users表创建成功")

                # 创建cookies表
                logging.info("创建cookies表...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS cookies (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(50) NOT NULL,
                        cookie_data JSON NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (username) REFERENCES users(username)
                    )
                """)
                logging.info("cookies表创建成功")

                # 创建area_codes表
                logging.info("创建area_codes表...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS area_codes (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        region VARCHAR(50) NOT NULL,
                        province VARCHAR(50) NOT NULL,
                        city VARCHAR(50),
                        code INT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE KEY unique_area (region, province, city)
                    )
                """)
                logging.info("area_codes表创建成功")

            self.connection.commit()
            logging.info("所有数据库表创建成功")
            
            # 验证表是否存在
            with self.connection.cursor() as cursor:
                cursor.execute("SHOW TABLES LIKE 'users'")
                if cursor.fetchone():
                    logging.info("users表已存在")
                else:
                    logging.error("users表创建失败")
                    
                cursor.execute("SHOW TABLES LIKE 'cookies'")
                if cursor.fetchone():
                    logging.info("cookies表已存在")
                else:
                    logging.error("cookies表创建失败")
                    
                cursor.execute("SHOW TABLES LIKE 'area_codes'")
                if cursor.fetchone():
                    logging.info("area_codes表已存在")
                else:
                    logging.error("area_codes表创建失败")
                    
        except Exception as e:
            logging.error(f"创建数据库表失败: {str(e)}")
            raise

    def save_cookies(self, username, cookies_dict):
        """保存cookies到数据库"""
        try:
            with self.connection.cursor() as cursor:
                # 检查是否存在旧记录
                cursor.execute("SELECT id FROM cookies WHERE username = %s", (username,))
                result = cursor.fetchone()

                if result:
                    # 更新现有记录
                    cursor.execute("""
                        UPDATE cookies 
                        SET cookie_data = %s, created_at = CURRENT_TIMESTAMP 
                        WHERE username = %s
                    """, (json.dumps(cookies_dict), username))
                else:
                    # 插入新记录
                    cursor.execute("""
                        INSERT INTO cookies (username, cookie_data)
                        VALUES (%s, %s)
                    """, (username, json.dumps(cookies_dict)))

                self.connection.commit()
                logging.info(f"成功保存用户 {username} 的cookies")
                return True
        except Exception as e:
            logging.error(f"保存cookies失败: {str(e)}")
            return False

    def get_cookies(self, username):
        """获取用户的cookies"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    SELECT cookie_data, created_at 
                    FROM cookies 
                    WHERE username = %s
                """, (username,))
                result = cursor.fetchone()
                
                if result:
                    cookie_data, created_at = result
                    # 检查cookies是否过期（30分钟）
                    if (datetime.now() - created_at).total_seconds() > 1800:
                        logging.info(f"用户 {username} 的cookies已过期")
                        return None
                    return json.loads(cookie_data)
                return None
        except Exception as e:
            logging.error(f"获取cookies失败: {str(e)}")
            return None

    def save_area_code(self, region, province, city, code):
        """
        保存地区码到数据库
        :param region: 地区（如：华北、华东等）
        :param province: 省份
        :param city: 城市（可以为None）
        :param code: 地区码
        :return: 是否保存成功
        """
        try:
            with self.connection.cursor() as cursor:
                sql = """
                    INSERT INTO area_codes (region, province, city, code)
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE code = %s
                """
                cursor.execute(sql, (region, province, city, code, code))
                self.connection.commit()
                return True
        except Exception as e:
            logging.error(f"保存地区码失败: {str(e)}")
            return False

    def get_area_code(self, region=None, province=None, city=None):
        """
        从数据库获取地区码
        :param region: 地区（如：华北、华东等）
        :param province: 省份
        :param city: 城市
        :return: 地区码，如果未找到返回None
        """
        try:
            with self.connection.cursor() as cursor:
                conditions = []
                params = []
                
                if region:
                    conditions.append("region = %s")
                    params.append(region)
                if province:
                    conditions.append("province = %s")
                    params.append(province)
                if city:
                    conditions.append("city = %s")
                    params.append(city)
                
                where_clause = " AND ".join(conditions) if conditions else "1"
                sql = f"SELECT code FROM area_codes WHERE {where_clause}"
                
                cursor.execute(sql, tuple(params))
                result = cursor.fetchone()
                return result[0] if result else None
        except Exception as e:
            logging.error(f"获取地区码失败: {str(e)}")
            return None

    def verify_area_code(self, code):
        """
        验证地区码是否存在于数据库中
        :param code: 地区码
        :return: 是否存在
        """
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT 1 FROM area_codes WHERE code = %s", (code,))
                return cursor.fetchone() is not None
        except Exception as e:
            logging.error(f"验证地区码失败: {str(e)}")
            return False

    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            logging.debug("数据库连接已关闭")

    def test_connection(self):
        """测试数据库连接"""
        try:
            if self.connection:
                with self.connection.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    result = cursor.fetchone()
                    if result:
                        logging.info("数据库连接测试成功！")
                        return True
            return False
        except Exception as e:
            logging.error(f"数据库连接测试失败：{str(e)}")
            return False

class DatabaseManager:
    def __init__(self):
        # 获取项目根目录
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # 创建data目录（如果不存在）
        data_dir = os.path.join(root_dir, 'data')
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        # 数据库文件路径
        self.db_path = os.path.join(data_dir, 'baidu_index.db')
        print(f"数据库路径: {self.db_path}")
        self.init_database()

    def init_database(self):
        """初始化数据库，创建必要的表"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 创建需求图谱数据表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS human_request_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                pv INTEGER,
                ratio INTEGER,
                sim INTEGER,
                keyword TEXT NOT NULL,
                date DATE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            conn.commit()
            print("数据库表创建成功")
        except Exception as e:
            print(f"创建数据库表时出错: {str(e)}")
        finally:
            conn.close()

    def save_human_request_data(self, data_list, keyword, date):
        """保存需求图谱数据到数据库"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 准备插入语句
            insert_sql = '''
            INSERT INTO human_request_data (word, pv, ratio, sim, keyword, date)
            VALUES (?, ?, ?, ?, ?, ?)
            '''
            
            # 批量插入数据
            for item in data_list:
                try:
                    cursor.execute(insert_sql, (
                        item.get('word', ''),
                        item.get('pv', 0),
                        item.get('ratio', 0),
                        item.get('sim', 0),
                        keyword,
                        date
                    ))
                except Exception as e:
                    print(f"插入数据时出错: {str(e)}")
                    print(f"问题数据: {item}")
            
            conn.commit()
            print(f"成功保存 {len(data_list)} 条数据")
            return True
        except Exception as e:
            print(f"保存数据到数据库时出错: {str(e)}")
            return False
        finally:
            conn.close()

    def get_human_request_data(self, keyword=None, start_date=None, end_date=None):
        """获取需求图谱数据"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = "SELECT * FROM human_request_data WHERE 1=1"
            params = []
            
            if keyword:
                query += " AND keyword = ?"
                params.append(keyword)
            if start_date:
                query += " AND date >= ?"
                params.append(start_date)
            if end_date:
                query += " AND date <= ?"
                params.append(end_date)
                
            query += " ORDER BY date DESC, id DESC"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            print(f"查询到 {len(results)} 条数据")
            return results
        except Exception as e:
            print(f"从数据库获取数据时出错: {str(e)}")
            return []
        finally:
            conn.close()

# 测试代码
if __name__ == "__main__":
    try:
        db = DatabaseConnection()
        if db.test_connection():
            print("数据库连接测试成功！")
        else:
            print("数据库连接测试失败！")
    except Exception as e:
        print(f"测试过程中出错: {str(e)}")
    finally:
        if 'db' in locals():
            db.close() 