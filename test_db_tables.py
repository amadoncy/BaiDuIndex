#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试数据库表
"""

import logging
import sys
import traceback
from config.database import DB_CONFIG
import pymysql

# 配置日志，直接输出到控制台
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
                    handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

def test_db_tables():
    """测试数据库表"""
    print("开始测试数据库表...")
    
    connection = None
    try:
        # 连接数据库
        print("连接数据库...")
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['db'],
            charset=DB_CONFIG['charset'],
            connect_timeout=5
        )
        
        cursor = connection.cursor()
        
        # 查询所有表
        cursor.execute("SHOW TABLES")
        existing_tables = {table[0] for table in cursor.fetchall()}
        print(f"现有表: {existing_tables}")
        
        # 要检查的表列表
        required_tables = [
            'baidu_index_trends',
            'crowd_age_data',
            'crowd_gender_data',
            'crowd_region_data',
            'human_request_data',
            'area_codes',
            'users',
            'cookies'
        ]
        
        # 检查是否所有表都存在
        missing_tables = [table for table in required_tables if table not in existing_tables]
        
        if missing_tables:
            print(f"缺少下列表: {missing_tables}")
            
            # 创建缺少的表
            for table in missing_tables:
                print(f"创建表 '{table}'...")
                
                if table == 'baidu_index_trends':
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS baidu_index_trends (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            date DATE NOT NULL,
                            index_value INT NOT NULL,
                            area VARCHAR(50) NOT NULL DEFAULT '全国',
                            keyword VARCHAR(100) NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE KEY unique_trend (date, area, keyword)
                        )
                    """)
                    
                elif table == 'crowd_age_data':
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS crowd_age_data (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            typeId INT NOT NULL,
                            name VARCHAR(50) NOT NULL,
                            tgi FLOAT NOT NULL,
                            rate FLOAT NOT NULL,
                            keyword VARCHAR(100) NOT NULL,
                            date DATE NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE KEY unique_age (name, keyword, date)
                        )
                    """)
                    
                elif table == 'crowd_gender_data':
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS crowd_gender_data (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            typeId INT NOT NULL,
                            name VARCHAR(50) NOT NULL,
                            tgi FLOAT NOT NULL,
                            rate FLOAT NOT NULL,
                            keyword VARCHAR(100) NOT NULL,
                            date DATE NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE KEY unique_gender (name, keyword, date)
                        )
                    """)
                    
                elif table == 'crowd_region_data':
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS crowd_region_data (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            province VARCHAR(50) NOT NULL,
                            value INT NOT NULL,
                            keyword VARCHAR(100) NOT NULL,
                            date DATE NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE KEY unique_region (province, keyword, date)
                        )
                    """)
                    
                elif table == 'human_request_data':
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS human_request_data (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            word VARCHAR(255) NOT NULL,
                            pv INT DEFAULT NULL,
                            ratio DECIMAL(10,2) DEFAULT NULL,
                            sim DECIMAL(10,2) DEFAULT NULL,
                            keyword VARCHAR(255) NOT NULL,
                            date DATE NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
                    
                elif table == 'area_codes':
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS area_codes (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            region VARCHAR(50) NOT NULL,
                            province VARCHAR(50) NOT NULL,
                            city VARCHAR(50) DEFAULT NULL,
                            code INT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE KEY unique_area (region, province, city)
                        )
                    """)
                    
                elif table == 'users':
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS users (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            username VARCHAR(50) NOT NULL,
                            password VARCHAR(255) NOT NULL,
                            phone VARCHAR(20) NOT NULL,
                            email VARCHAR(100) NOT NULL,
                            last_login DATETIME DEFAULT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                            UNIQUE KEY username (username),
                            UNIQUE KEY phone (phone),
                            UNIQUE KEY email (email)
                        )
                    """)
                    
                elif table == 'cookies':
                    cursor.execute("""
                        CREATE TABLE IF NOT EXISTS cookies (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            username VARCHAR(50) NOT NULL,
                            cookie_data JSON NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """)
            
            # 提交所有更改
            connection.commit()
            
            # 重新检查表
            cursor.execute("SHOW TABLES")
            updated_tables = {table[0] for table in cursor.fetchall()}
            print(f"更新后的表: {updated_tables}")
        else:
            print("所有必要的表都已存在")
        
        # 检查每个表的结构
        print("检查表的结构...")
        
        for table in required_tables:
            print(f"\n表 '{table}' 的结构:")
            cursor.execute(f"DESCRIBE {table}")
            columns = cursor.fetchall()
            for column in columns:
                print(f"  - {column}")
        
        cursor.close()
        connection.close()
        print("数据库连接已关闭")
        
        return True
        
    except Exception as e:
        print(f"发生错误: {str(e)}")
        traceback.print_exc()
        return False
    finally:
        if connection and connection.open:
            connection.close()
            print("已关闭数据库连接")

if __name__ == "__main__":
    try:
        result = test_db_tables()
        if result:
            print("数据库表测试成功!")
            sys.exit(0)
        else:
            print("数据库表测试失败!")
            sys.exit(1)
    except Exception as e:
        print(f"程序执行错误: {str(e)}")
        traceback.print_exc()
        sys.exit(1) 