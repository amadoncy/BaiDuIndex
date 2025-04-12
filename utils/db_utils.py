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
            logging.debug(
                f"连接信息: host={DB_CONFIG['host']}, port={DB_CONFIG['port']}, user={DB_CONFIG['user']}, database={DB_CONFIG['db']}")

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

                # 创建关键词聚类表
                logging.info("创建keyword_clusters表...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS keyword_clusters (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        base_keyword VARCHAR(100) NOT NULL,
                        cluster_name VARCHAR(50) NOT NULL,
                        keyword VARCHAR(100) NOT NULL,
                        similarity FLOAT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_base_keyword (base_keyword)
                    )
                """)
                logging.info("keyword_clusters表创建成功")

                # 创建用户行为聚类表
                logging.info("创建behavior_clusters表...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS behavior_clusters (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        keyword VARCHAR(100) NOT NULL,
                        cluster_name VARCHAR(50) NOT NULL,
                        behavior_type VARCHAR(50) NOT NULL,
                        ratio FLOAT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_keyword (keyword)
                    )
                """)
                logging.info("behavior_clusters表创建成功")

                # 创建趋势预测表
                logging.info("创建trend_predictions表...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS trend_predictions (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        keyword VARCHAR(100) NOT NULL,
                        prediction_date DATE NOT NULL,
                        predicted_index INT NOT NULL,
                        confidence FLOAT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_keyword (keyword)
                    )
                """)
                logging.info("trend_predictions表创建成功")

                # 创建需求预测表
                logging.info("创建demand_predictions表...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS demand_predictions (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        keyword VARCHAR(100) NOT NULL,
                        predicted_demand VARCHAR(100) NOT NULL,
                        probability FLOAT NOT NULL,
                        growth_trend VARCHAR(20) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_keyword (keyword)
                    )
                """)
                logging.info("demand_predictions表创建成功")

                # 创建竞品搜索指数表
                logging.info("创建competitor_search_index表...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS competitor_search_index (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        keyword VARCHAR(100) NOT NULL,
                        competitor_name VARCHAR(100) NOT NULL,
                        search_index INT NOT NULL,
                        market_share FLOAT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_keyword (keyword)
                    )
                """)
                logging.info("competitor_search_index表创建成功")

                # 创建竞品用户重叠表
                logging.info("创建competitor_user_overlap表...")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS competitor_user_overlap (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        keyword VARCHAR(100) NOT NULL,
                        competitor_name VARCHAR(100) NOT NULL,
                        user_overlap FLOAT NOT NULL,
                        competition_level VARCHAR(20) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        INDEX idx_keyword (keyword)
                    )
                """)
                logging.info("competitor_user_overlap表创建成功")

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
            with self.connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            logging.error(f"数据库连接测试失败: {str(e)}")
            return False

    def clear_database(self):
        """清空数据库表内容，但保留users、area_codes和cookies表的数据"""
        try:
            with self.connection.cursor() as cursor:
                # 获取所有表名
                cursor.execute("SHOW TABLES")
                tables = [table[0] for table in cursor.fetchall()]

                # 排除需要保留的表
                excluded_tables = ['users', 'area_codes', 'cookies']
                tables_to_clear = [table for table in tables if table not in excluded_tables]

                # 临时禁用外键检查
                cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

                # 清空所有不需要保留的表
                for table in tables_to_clear:
                    cursor.execute(f"TRUNCATE TABLE `{table}`")
                    logging.info(f"已清空表: {table}")

                # 重新启用外键检查
                cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

                self.connection.commit()
                return True, tables_to_clear
        except Exception as e:
            logging.error(f"清空数据库表失败: {str(e)}")
            return False, []

    def get_trend_data(self, keyword):
        """获取趋势数据"""
        try:
            query = """
                SELECT date, index_value
                FROM baidu_index_trends
                WHERE keyword = %s
                ORDER BY date DESC
            """
            self.cursor.execute(query, (keyword,))
            results = self.cursor.fetchall()
            return [{'date': row[0], 'index': row[1]} for row in results]
        except Exception as e:
            logging.error(f"获取趋势数据失败: {str(e)}")
            return []

    def get_portrait_data(self, keyword):
        """获取人群画像数据"""
        try:
            # 获取年龄分布数据
            age_query = """
                SELECT name, rate
                FROM crowd_age_data
                WHERE keyword = %s
                ORDER BY created_at DESC
            """
            self.cursor.execute(age_query, (keyword,))
            age_results = self.cursor.fetchall()
            
            # 获取性别分布数据
            gender_query = """
                SELECT name, rate
                FROM crowd_gender_data
                WHERE keyword = %s
                ORDER BY created_at DESC
            """
            self.cursor.execute(gender_query, (keyword,))
            gender_results = self.cursor.fetchall()
            
            # 获取兴趣分布数据
            interest_query = """
                SELECT name, rate
                FROM crowd_interest_data
                WHERE keyword = %s
                ORDER BY created_at DESC
            """
            self.cursor.execute(interest_query, (keyword,))
            interest_results = self.cursor.fetchall()
            
            return {
                'age': [{'range': row[0], 'ratio': row[1]} for row in age_results],
                'gender': [{'type': row[0], 'ratio': row[1]} for row in gender_results],
                'interest': [{'type': row[0], 'ratio': row[1]} for row in interest_results]
            }
        except Exception as e:
            logging.error(f"获取人群画像数据失败: {str(e)}")
            return None

    def get_demand_data(self, keyword):
        """获取需求分布数据"""
        try:
            query = """
                SELECT word, pv, ratio, sim
                FROM human_request_data
                WHERE keyword = %s
                ORDER BY pv DESC
            """
            self.cursor.execute(query, (keyword,))
            results = self.cursor.fetchall()
            return [{'word': row[0], 'pv': row[1], 'ratio': row[2], 'sim': row[3]} for row in results]
        except Exception as e:
            logging.error(f"获取需求分布数据失败: {str(e)}")
            return []

    def get_region_data(self, keyword):
        """获取地域分布数据"""
        try:
            query = """
                SELECT province, value
                FROM crowd_region_data
                WHERE keyword = %s
                ORDER BY value DESC
            """
            self.cursor.execute(query, (keyword,))
            results = self.cursor.fetchall()
            return [{'province': row[0], 'value': row[1]} for row in results]
        except Exception as e:
            logging.error(f"获取地域分布数据失败: {str(e)}")
            return []

    def get_cluster_data(self, keyword):
        """获取聚类分析数据"""
        try:
            # 获取关键词聚类数据
            keyword_query = """
                SELECT cluster_name, keyword, similarity
                FROM keyword_clusters
                WHERE base_keyword = %s
                ORDER BY cluster_name, similarity DESC
            """
            self.cursor.execute(keyword_query, (keyword,))
            keyword_results = self.cursor.fetchall()
            
            # 获取用户行为聚类数据
            behavior_query = """
                SELECT cluster_name, behavior_type, ratio
                FROM behavior_clusters
                WHERE keyword = %s
                ORDER BY cluster_name, ratio DESC
            """
            self.cursor.execute(behavior_query, (keyword,))
            behavior_results = self.cursor.fetchall()
            
            return {
                'keywords': [{'cluster': row[0], 'keyword': row[1], 'similarity': row[2]} for row in keyword_results],
                'behaviors': [{'cluster': row[0], 'behavior': row[1], 'ratio': row[2]} for row in behavior_results]
            }
        except Exception as e:
            logging.error(f"获取聚类分析数据失败: {str(e)}")
            return {'keywords': [], 'behaviors': []}

    def get_prediction_data(self, keyword):
        """获取预测分析数据"""
        try:
            # 获取趋势预测数据
            trend_query = """
                SELECT prediction_date, predicted_index, confidence
                FROM trend_predictions
                WHERE keyword = %s
                ORDER BY prediction_date
            """
            self.cursor.execute(trend_query, (keyword,))
            trend_results = self.cursor.fetchall()
            
            # 获取需求预测数据
            demand_query = """
                SELECT predicted_demand, probability, growth_trend
                FROM demand_predictions
                WHERE keyword = %s
                ORDER BY probability DESC
            """
            self.cursor.execute(demand_query, (keyword,))
            demand_results = self.cursor.fetchall()
            
            return {
                'trend': [{'date': row[0], 'index': row[1], 'confidence': row[2]} for row in trend_results],
                'demands': [{'demand': row[0], 'probability': row[1], 'trend': row[2]} for row in demand_results]
            }
        except Exception as e:
            logging.error(f"获取预测分析数据失败: {str(e)}")
            return {'trend': [], 'demands': []}

    def get_competitor_data(self, keyword):
        """获取竞品分析数据"""
        try:
            # 获取竞品搜索指数数据
            index_query = """
                SELECT competitor_name, search_index, market_share
                FROM competitor_search_index
                WHERE keyword = %s
                ORDER BY search_index DESC
            """
            self.cursor.execute(index_query, (keyword,))
            index_results = self.cursor.fetchall()
            
            # 获取用户重叠度数据
            overlap_query = """
                SELECT competitor_name, user_overlap, competition_level
                FROM competitor_user_overlap
                WHERE keyword = %s
                ORDER BY user_overlap DESC
            """
            self.cursor.execute(overlap_query, (keyword,))
            overlap_results = self.cursor.fetchall()
            
            return {
                'search_index': [{'competitor': row[0], 'index': row[1], 'market_share': row[2]} for row in index_results],
                'user_overlap': [{'competitor': row[0], 'overlap': row[1], 'competition': row[2]} for row in overlap_results]
            }
        except Exception as e:
            logging.error(f"获取竞品分析数据失败: {str(e)}")
            return {'search_index': [], 'user_overlap': []}


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


def get_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['db'],
            charset=DB_CONFIG['charset']
        )
        return connection
    except Exception as e:
        logging.error(f"数据库连接失败: {str(e)}")
        raise


def execute_query(query, params=None):
    """执行查询语句"""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(query, params)
        results = cursor.fetchall()
        cursor.close()
        connection.close()
        return results
    except Exception as e:
        logging.error(f"执行查询失败: {str(e)}")
        raise


def execute_update(query, params=None):
    """执行更新语句"""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(query, params)
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        logging.error(f"执行更新失败: {str(e)}")
        raise


def execute_many(query, params_list):
    """执行批量更新语句"""
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.executemany(query, params_list)
        connection.commit()
        cursor.close()
        connection.close()
    except Exception as e:
        logging.error(f"执行批量更新失败: {str(e)}")
        raise


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