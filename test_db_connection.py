#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试数据库连接的简单脚本
"""

import sys
import traceback
from config.database import DB_CONFIG
import pymysql

def test_db_connection():
    """测试数据库连接"""
    print("开始测试数据库连接...")
    
    connection = None
    try:
        # 连接数据库
        print("尝试连接数据库...")
        print(f"配置信息: 主机={DB_CONFIG['host']}, 端口={DB_CONFIG['port']}, 数据库={DB_CONFIG['db']}")
        
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['db'],
            charset=DB_CONFIG['charset'],
            connect_timeout=5
        )
        
        print("数据库连接成功!")
        
        # 执行简单查询
        cursor = connection.cursor()
        print("执行查询: SELECT VERSION()")
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        print(f"数据库版本: {version[0]}")
        
        # 检查表
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()
        print(f"数据库中的表: {[table[0] for table in tables]}")
        
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
        result = test_db_connection()
        if result:
            print("数据库连接测试成功!")
            sys.exit(0)
        else:
            print("数据库连接测试失败!")
            sys.exit(1)
    except Exception as e:
        print(f"程序执行错误: {str(e)}")
        traceback.print_exc()
        sys.exit(1) 