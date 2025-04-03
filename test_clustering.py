#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试聚类功能
"""

import os
import sys
import logging
import traceback
from utils.clustering_utils import ClusteringUtils
from utils import db_utils
import pandas as pd
import datetime

# 预检查必要的依赖
try:
    import matplotlib
    print(f"使用 matplotlib 版本: {matplotlib.__version__}")
    # 设置为非交互模式，避免弹出窗口
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    print("matplotlib 导入成功")
except ImportError as e:
    print(f"matplotlib 导入错误: {str(e)}")
    sys.exit(1)

# 配置日志
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(levelname)s - %(module)s - %(message)s',
                   handlers=[logging.StreamHandler()])
logger = logging.getLogger(__name__)

# 强制将日志设置为DEBUG级别
for handler in logging.root.handlers:
    handler.setLevel(logging.DEBUG)

# 为关键包设置日志级别
logging.getLogger('utils.clustering_utils').setLevel(logging.DEBUG)
logging.getLogger('utils.db_utils').setLevel(logging.DEBUG)

# 添加文件日志
file_handler = logging.FileHandler('clustering_test.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(message)s'))
logging.getLogger().addHandler(file_handler)

def setup_test_data():
    """
    准备测试数据，如果数据表中没有数据则添加一些测试数据
    """
    try:
        conn = db_utils.get_connection()
        if not conn:
            logger.error("数据库连接失败")
            return False
            
        cursor = conn.cursor()
        
        # 检查关键词趋势表是否有数据
        cursor.execute("SELECT COUNT(*) FROM baidu_index_trends")
        count = cursor.fetchone()[0]
        
        # 如果没有数据，添加测试数据
        if count == 0:
            logger.info("百度指数趋势表中没有数据，添加测试数据...")
            
            # 创建一些测试关键词
            keywords = ["苹果", "华为", "小米", "三星", "OPPO", "vivo", "魅族"]
            areas = ["全国", "北京", "上海", "广州", "深圳"]
            
            # 添加测试数据 - 百度指数趋势
            for keyword in keywords:
                # 获取最近30天的日期
                today = datetime.date.today()
                for i in range(30):
                    date = (today - datetime.timedelta(days=i)).strftime("%Y-%m-%d")
                    for area in areas:
                        index_value = 500 + (100 * keywords.index(keyword)) + (i * 10)
                        
                        # 添加一些随机性使数据更真实
                        import random
                        index_value += random.randint(-50, 50)
                        
                        try:
                            cursor.execute("""
                                INSERT INTO baidu_index_trends (date, index_value, area, keyword)
                                VALUES (%s, %s, %s, %s)
                                ON DUPLICATE KEY UPDATE index_value = VALUES(index_value)
                            """, (date, index_value, area, keyword))
                        except Exception as e:
                            # 如果重复键错误，跳过
                            logger.warning(f"添加指数数据时出现错误: {str(e)}")
                            continue
            
            # 添加测试数据 - 年龄分布
            age_groups = ["19岁以下", "20-29岁", "30-39岁", "40-49岁", "50岁以上"]
            cursor.execute("SELECT COUNT(*) FROM crowd_age_data")
            if cursor.fetchone()[0] == 0:
                logger.info("年龄分布表中没有数据，添加测试数据...")
                for keyword in keywords:
                    date = today.strftime("%Y-%m-%d")
                    # 为每个关键词分配不同的年龄分布
                    for i, age in enumerate(age_groups):
                        typeId = i + 1
                        # 不同关键词有不同的主要年龄群体
                        rate = 0.1
                        if i == keywords.index(keyword) % len(age_groups):
                            rate = 0.4  # 主要年龄群体
                        elif i == (keywords.index(keyword) + 1) % len(age_groups):
                            rate = 0.25  # 次要年龄群体
                        
                        # TGI指数 - 目标群体中占比 / 总体中占比 * 100
                        tgi = rate / 0.2 * 100  # 假设整体平均每个群体占比是0.2
                        
                        try:
                            cursor.execute("""
                                INSERT INTO crowd_age_data (typeId, name, tgi, rate, keyword, date)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                ON DUPLICATE KEY UPDATE tgi = VALUES(tgi), rate = VALUES(rate)
                            """, (typeId, age, tgi, rate, keyword, date))
                        except Exception as e:
                            logger.warning(f"添加年龄数据时出现错误: {str(e)}")
                            continue
            
            # 添加测试数据 - 性别分布
            cursor.execute("SELECT COUNT(*) FROM crowd_gender_data")
            if cursor.fetchone()[0] == 0:
                logger.info("性别分布表中没有数据，添加测试数据...")
                for keyword in keywords:
                    date = today.strftime("%Y-%m-%d")
                    
                    # 为不同关键词设置不同的性别比例
                    male_rate = 0.5
                    if keywords.index(keyword) % 3 == 0:
                        male_rate = 0.7  # 男性较多
                    elif keywords.index(keyword) % 3 == 1:
                        male_rate = 0.3  # 女性较多
                    
                    female_rate = 1 - male_rate
                    
                    # 男性数据
                    male_tgi = male_rate / 0.5 * 100
                    try:
                        cursor.execute("""
                            INSERT INTO crowd_gender_data (typeId, name, tgi, rate, keyword, date)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE tgi = VALUES(tgi), rate = VALUES(rate)
                        """, (1, "男", male_tgi, male_rate, keyword, date))
                    except Exception as e:
                        logger.warning(f"添加性别数据时出现错误: {str(e)}")
                    
                    # 女性数据
                    female_tgi = female_rate / 0.5 * 100
                    try:
                        cursor.execute("""
                            INSERT INTO crowd_gender_data (typeId, name, tgi, rate, keyword, date)
                            VALUES (%s, %s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE tgi = VALUES(tgi), rate = VALUES(rate)
                        """, (2, "女", female_tgi, female_rate, keyword, date))
                    except Exception as e:
                        logger.warning(f"添加性别数据时出现错误: {str(e)}")
            
            # 添加测试数据 - 地域分布
            cursor.execute("SELECT COUNT(*) FROM crowd_region_data")
            if cursor.fetchone()[0] == 0:
                logger.info("地域分布表中没有数据，添加测试数据...")
                provinces = ["北京", "上海", "广东", "浙江", "江苏", "四川", "湖北", "湖南", "河南", "山东"]
                for keyword in keywords:
                    date = today.strftime("%Y-%m-%d")
                    
                    # 为每个关键词分配不同的地域分布
                    for i, province in enumerate(provinces):
                        # 不同的关键词在不同地域有不同的热度
                        value = 100
                        if i == keywords.index(keyword) % len(provinces):
                            value = 500  # 主要地域
                        elif i == (keywords.index(keyword) + 1) % len(provinces):
                            value = 300  # 次要地域
                        
                        try:
                            cursor.execute("""
                                INSERT INTO crowd_region_data (province, value, keyword, date)
                                VALUES (%s, %s, %s, %s)
                                ON DUPLICATE KEY UPDATE value = VALUES(value)
                            """, (province, value, keyword, date))
                        except Exception as e:
                            logger.warning(f"添加地域数据时出现错误: {str(e)}")
                            continue
            
            # 添加测试数据 - 人群需求数据
            cursor.execute("SELECT COUNT(*) FROM human_request_data")
            if cursor.fetchone()[0] == 0:
                logger.info("人群需求表中没有数据，添加测试数据...")
                for keyword in keywords:
                    date = today.strftime("%Y-%m-%d")
                    
                    # 为每个关键词添加3-5个相关搜索词
                    related_words = []
                    if keyword == "苹果":
                        related_words = ["iPhone", "MacBook", "iPad", "AirPods", "iOS"]
                    elif keyword == "华为":
                        related_words = ["Mate", "P40", "鸿蒙", "华为手表", "华为平板"]
                    elif keyword == "小米":
                        related_words = ["红米", "MIUI", "小米11", "小米手环", "小米电视"]
                    else:
                        # 为其他关键词生成通用相关词
                        related_words = [f"{keyword}手机", f"{keyword}新品", f"{keyword}价格", 
                                       f"{keyword}评测", f"{keyword}配置"]
                    
                    for word in related_words:
                        pv = 1000 + keywords.index(keyword) * 100 + related_words.index(word) * 50
                        ratio = round(pv / 5000.0, 2)  # 相对比例
                        sim = round(0.5 + related_words.index(word) * 0.1, 2)  # 相似度
                        
                        try:
                            cursor.execute("""
                                INSERT INTO human_request_data (word, pv, ratio, sim, keyword, date)
                                VALUES (%s, %s, %s, %s, %s, %s)
                                ON DUPLICATE KEY UPDATE pv = VALUES(pv), ratio = VALUES(ratio), sim = VALUES(sim)
                            """, (word, pv, ratio, sim, keyword, date))
                        except Exception as e:
                            logger.warning(f"添加人群需求数据时出现错误: {str(e)}")
                            continue
            
            conn.commit()
            logger.info("测试数据添加完成")
        else:
            logger.info(f"百度指数趋势表已有数据，共{count}条记录")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"准备测试数据失败: {str(e)}")
        traceback.print_exc()
        return False

def test_keyword_clustering():
    """测试关键词聚类功能"""
    try:
        print("开始测试关键词聚类...")
        logger.info("开始测试关键词聚类...")
        
        # 创建聚类工具实例
        print("实例化聚类工具...")
        clustering_utils = ClusteringUtils()
        
        # 执行关键词聚类
        print("执行关键词聚类分析...")
        try:
            results, message = clustering_utils.keyword_clustering(n_clusters=3)
            print("关键词聚类分析执行完成.")
        except Exception as e:
            print(f"关键词聚类分析执行失败: {str(e)}")
            logger.error(f"关键词聚类分析执行失败: {str(e)}")
            traceback.print_exc()
            return False
        
        if results:
            print(f"聚类成功: {message}")
            print(f"得到 {len(results['clusters'])} 个聚类组")
            for cluster_id, keywords in results['clusters'].items():
                print(f"  - 聚类 {cluster_id}: {len(keywords)} 个关键词")
                
            print(f"可视化文件: {results['visualization']}")
            print("特征重要性:")
            for feature, importance in results['feature_importance'].items():
                print(f"  - {feature}: {importance:.4f}")
                
            logger.info(f"聚类成功: {message}")
            logger.info(f"聚类结果: {results['clusters']}")
            logger.info(f"可视化文件: {results['visualization']}")
            logger.info(f"特征重要性: {results['feature_importance']}")
            return True
        else:
            print(f"聚类失败: {message}")
            logger.error(f"聚类失败: {message}")
            return False
    
    except Exception as e:
        print(f"关键词聚类测试失败: {str(e)}")
        logger.error(f"关键词聚类测试失败: {str(e)}")
        traceback.print_exc()
        return False

def test_user_behavior_clustering():
    """测试用户行为聚类功能"""
    try:
        print("开始测试用户行为聚类...")
        logger.info("开始测试用户行为聚类...")
        
        # 创建聚类工具实例
        print("实例化聚类工具...")
        clustering_utils = ClusteringUtils()
        
        # 执行用户行为聚类
        print("执行用户行为聚类分析...")
        try:
            results, message = clustering_utils.user_behavior_clustering(n_clusters=2)
            print("用户行为聚类分析执行完成.")
        except Exception as e:
            print(f"用户行为聚类分析执行失败: {str(e)}")
            logger.error(f"用户行为聚类分析执行失败: {str(e)}")
            traceback.print_exc()
            return False
        
        if results:
            print(f"用户行为聚类成功: {message}")
            print(f"得到 {len(results['clusters'])} 个聚类组")
            for cluster_id, keywords in results['clusters'].items():
                print(f"  - 聚类 {cluster_id}: {len(keywords)} 个关键词")
                
            print(f"可视化文件: {results['visualization']}")
            
            if 'cluster_analysis' in results:
                print("聚类分析:")
                for cluster_id, analysis in results['cluster_analysis'].items():
                    print(f"  - 聚类 {cluster_id}: {analysis}")
            
            logger.info(f"用户行为聚类成功: {message}")
            logger.info(f"聚类结果: {results['clusters']}")
            logger.info(f"可视化文件: {results['visualization']}")
            
            if 'cluster_analysis' in results:
                logger.info(f"聚类分析: {results['cluster_analysis']}")
            
            return True
        else:
            print(f"用户行为聚类失败: {message}")
            logger.error(f"用户行为聚类失败: {message}")
            return False
    
    except Exception as e:
        print(f"用户行为聚类测试失败: {str(e)}")
        logger.error(f"用户行为聚类测试失败: {str(e)}")
        traceback.print_exc()
        return False

def test_db_connection():
    """测试数据库连接"""
    print("测试数据库连接...")
    try:
        connection = db_utils.get_connection()
        if connection:
            print("数据库连接成功")
            
            # 尝试查询一个简单的SQL语句
            cursor = connection.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"数据库版本: {version[0]}")
            
            cursor.close()
            connection.close()
            print("数据库连接已关闭")
            return True
        else:
            print("数据库连接失败")
            return False
    except Exception as e:
        print(f"数据库连接错误: {str(e)}")
        traceback.print_exc()
        return False

def main():
    """主函数"""
    try:
        print("=" * 60)
        print("开始聚类功能测试...")
        logger.info("开始聚类功能测试...")
        
        # 首先测试数据库连接
        print("\n测试数据库连接...")
        if not test_db_connection():
            print("数据库连接测试失败，无法继续测试")
            return False
        print("数据库连接测试通过")
        
        # 创建数据目录
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, 'data')
        clusters_dir = os.path.join(data_dir, 'clusters')
        
        # 确保数据目录存在
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            print(f"创建数据目录: {data_dir}")
            
        if not os.path.exists(clusters_dir):
            os.makedirs(clusters_dir)
            print(f"创建聚类数据目录: {clusters_dir}")
            
        logger.info(f"数据目录: {data_dir}")
        logger.info(f"聚类数据目录: {clusters_dir}")
        
        # 准备测试数据
        print("准备测试数据...")
        if not setup_test_data():
            print("准备测试数据失败")
            logger.error("准备测试数据失败")
            return False
        print("测试数据准备完成")
        
        # 测试关键词聚类
        print("\n" + "-" * 40)
        print("开始测试关键词聚类...")
        keyword_result = test_keyword_clustering()
        if keyword_result:
            print("关键词聚类测试通过!")
        else:
            print("关键词聚类测试失败!")
        
        # 测试用户行为聚类
        print("\n" + "-" * 40)
        print("开始测试用户行为聚类...")
        user_result = test_user_behavior_clustering()
        if user_result:
            print("用户行为聚类测试通过!")
        else:
            print("用户行为聚类测试失败!")
        
        print("\n" + "=" * 60)
        if keyword_result and user_result:
            print("聚类功能测试全部通过!")
            logger.info("聚类功能测试全部通过!")
            return True
        else:
            print("部分聚类测试未通过")
            logger.warning("部分聚类测试未通过")
            return False
    
    except Exception as e:
        print(f"聚类测试失败: {str(e)}")
        logger.error(f"聚类测试失败: {str(e)}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("聚类功能测试成功完成!")
            sys.exit(0)
        else:
            print("聚类功能测试失败!")
            sys.exit(1)
    except Exception as e:
        print(f"程序执行错误: {str(e)}")
        traceback.print_exc()
        sys.exit(1) 