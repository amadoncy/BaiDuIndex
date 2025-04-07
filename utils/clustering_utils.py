import os
import logging
import pandas as pd
import numpy as np
from sklearn.cluster import KMeans, DBSCAN
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from utils import db_utils
from sklearn.metrics import silhouette_score
import datetime
import json
from pyecharts import options as opts
from pyecharts.charts import Scatter
import tempfile


class ClusteringUtils:
    """
    聚类分析工具类
    提供关键词聚类和用户行为聚类功能
    """

    def __init__(self):
        """初始化聚类工具类"""
        self.scaler = StandardScaler()
        self.logger = logging.getLogger(__name__)

    def keyword_clustering(self, keywords=None, n_clusters=3, method='kmeans'):
        """
        对关键词进行聚类分析

        Args:
            keywords (list): 要聚类的关键词列表。如果为None，将从数据库获取所有关键词
            n_clusters (int): 聚类数量
            method (str): 聚类方法，'kmeans'或'dbscan'

        Returns:
            dict: 聚类结果，格式为 {cluster_id: [keywords]}
        """
        try:
            # 连接数据库
            conn = db_utils.get_connection()
            if not conn:
                self.logger.error("数据库连接失败")
                return None, "数据库连接失败"

            cursor = conn.cursor()

            # 如果未提供关键词，则从数据库获取
            if not keywords:
                cursor.execute("SELECT DISTINCT keyword FROM baidu_index_trends")
                keywords_data = cursor.fetchall()
                keywords = [row[0] for row in keywords_data]

            if not keywords:
                return None, "没有可用的关键词数据"

            # 为每个关键词获取特征
            features = []
            valid_keywords = []

            for keyword in keywords:
                # 1. 获取趋势数据 - 计算平均值、波动性、最大值等
                cursor.execute("""
                    SELECT AVG(index_value), MAX(index_value), MIN(index_value), 
                           STDDEV(index_value), COUNT(index_value)
                    FROM baidu_index_trends 
                    WHERE keyword = %s
                """, (keyword,))
                trend_stats = cursor.fetchone()

                # 2. 获取人群画像数据 - 主要年龄组和性别比例
                cursor.execute("""
                    SELECT name, rate FROM crowd_age_data 
                    WHERE keyword = %s 
                    ORDER BY rate DESC LIMIT 1
                """, (keyword,))
                age_data = cursor.fetchone()

                cursor.execute("""
                    SELECT name, rate FROM crowd_gender_data 
                    WHERE keyword = %s AND name = '男'
                """, (keyword,))
                gender_data = cursor.fetchone()

                # 3. 获取区域数据 - 前三个区域的占比
                cursor.execute("""
                    SELECT SUM(value) FROM crowd_region_data 
                    WHERE keyword = %s 
                    ORDER BY value DESC LIMIT 3
                """, (keyword,))
                region_data = cursor.fetchone()

                # 4. 获取需求数据 - 相关搜索词数量
                cursor.execute("""
                    SELECT COUNT(*) FROM human_request_data 
                    WHERE keyword = %s
                """, (keyword,))
                request_count = cursor.fetchone()

                # 如果有足够数据，创建特征向量
                if (trend_stats and age_data and gender_data and
                        trend_stats[0] is not None and age_data[1] is not None and
                        gender_data[1] is not None):
                    feature_vector = [
                        float(trend_stats[0]) if trend_stats[0] is not None else 0,  # 平均指数
                        float(trend_stats[1]) if trend_stats[1] is not None else 0,  # 最大指数
                        float(trend_stats[2]) if trend_stats[2] is not None else 0,  # 最小指数
                        float(trend_stats[3]) if trend_stats[3] is not None else 0,  # 标准差
                        float(age_data[1]) if age_data[1] is not None else 0,  # 主要年龄组占比
                        float(gender_data[1]) if gender_data[1] is not None else 0,  # 男性占比
                        float(region_data[0]) if region_data and region_data[0] is not None else 0,  # 前三区域占比
                        float(request_count[0]) if request_count and request_count[0] is not None else 0  # 相关搜索词数量
                    ]

                    features.append(feature_vector)
                    valid_keywords.append(keyword)

            # 如果没有有效数据，返回错误
            if not features:
                return None, "没有足够的数据进行聚类分析"

            # 标准化特征
            X = self.scaler.fit_transform(features)

            # 使用PCA降维到2维，便于可视化
            pca = PCA(n_components=2)
            X_pca = pca.fit_transform(X)

            # 聚类分析
            labels = None
            if method.lower() == 'kmeans':
                # KMeans聚类
                kmeans = KMeans(n_clusters=n_clusters, random_state=42)
                labels = kmeans.fit_predict(X)

                # 评估聚类效果
                if len(set(labels)) > 1:  # 至少有两个聚类才能计算silhouette
                    silhouette_avg = silhouette_score(X, labels)
                    self.logger.info(f"聚类评分 (Silhouette): {silhouette_avg:.4f}")

            elif method.lower() == 'dbscan':
                # DBSCAN聚类 - 自动确定聚类数量
                dbscan = DBSCAN(eps=0.5, min_samples=2)
                labels = dbscan.fit_predict(X)

                # 统计聚类数量和噪声点
                n_clusters_actual = len(set(labels)) - (1 if -1 in labels else 0)
                n_noise = list(labels).count(-1)
                self.logger.info(f"DBSCAN聚类数量: {n_clusters_actual}，噪声点数量: {n_noise}")

            # 创建结果字典
            clusters = {}
            for i, label in enumerate(labels):
                if label not in clusters:
                    clusters[int(label)] = []
                clusters[int(label)].append(valid_keywords[i])

            # 生成可视化图表
            visualization_path = self._create_visualization(X_pca, labels, valid_keywords)

            # 关闭数据库连接
            cursor.close()
            conn.close()

            return {
                'clusters': clusters,
                'visualization': visualization_path,
                'feature_importance': self._get_feature_importance(pca)
            }, "聚类分析完成"

        except Exception as e:
            self.logger.error(f"关键词聚类失败: {str(e)}")
            return None, f"聚类失败: {str(e)}"

    def user_behavior_clustering(self, n_clusters=3):
        """
        对用户行为进行聚类分析

        Args:
            n_clusters (int): 聚类数量

        Returns:
            dict: 聚类结果和分析
        """
        try:
            # 连接数据库
            conn = db_utils.get_connection()
            if not conn:
                self.logger.error("数据库连接失败")
                return None, "数据库连接失败"

            cursor = conn.cursor()

            # 获取人群画像数据 - 年龄、性别、兴趣偏好
            cursor.execute("""
                SELECT DISTINCT keyword FROM crowd_age_data
            """)
            keywords = [row[0] for row in cursor.fetchall()]

            if not keywords:
                return None, "没有可用的用户行为数据"

            user_features = []
            valid_keywords = []

            for keyword in keywords:
                # 获取年龄分布数据
                cursor.execute("""
                    SELECT name, rate FROM crowd_age_data 
                    WHERE keyword = %s
                """, (keyword,))
                age_data = cursor.fetchall()

                # 获取性别分布数据
                cursor.execute("""
                    SELECT name, rate FROM crowd_gender_data 
                    WHERE keyword = %s
                """, (keyword,))
                gender_data = cursor.fetchall()

                # 处理兴趣分布数据 - 检查表是否存在
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM information_schema.tables 
                    WHERE table_schema = DATABASE() 
                    AND table_name = 'crowd_interest_data'
                """)
                if cursor.fetchone()[0] > 0:
                    cursor.execute("""
                        SELECT name, rate FROM crowd_interest_data 
                        WHERE keyword = %s 
                        ORDER BY rate DESC LIMIT 5
                    """, (keyword,))
                    interest_data = cursor.fetchall()
                else:
                    # 如果没有兴趣表，使用空列表
                    interest_data = []

                # 创建特征向量 - 使用年龄和性别分布作为特征
                if age_data and gender_data:
                    # 处理年龄特征 - 使用不同年龄段的占比
                    age_features = {}
                    for name, rate in age_data:
                        age_features[name] = float(rate) if rate is not None else 0

                    # 处理性别特征
                    gender_features = {}
                    for name, rate in gender_data:
                        gender_features[name] = float(rate) if rate is not None else 0

                    # 组合特征 - 可以根据需要调整
                    feature_vector = [
                        age_features.get('19岁以下', 0),
                        age_features.get('20-29岁', 0),
                        age_features.get('30-39岁', 0),
                        age_features.get('40-49岁', 0),
                        age_features.get('50岁以上', 0),
                        gender_features.get('男', 0),
                        gender_features.get('女', 0)
                    ]

                    # 添加兴趣特征 (可选)
                    interest_rate_sum = sum([float(rate) for _, rate in interest_data]) if interest_data else 0
                    if interest_rate_sum > 0:
                        feature_vector.append(interest_rate_sum / len(interest_data))
                    else:
                        feature_vector.append(0)

                    user_features.append(feature_vector)
                    valid_keywords.append(keyword)

            # 如果没有有效数据，返回错误
            if not user_features:
                return None, "没有足够的用户行为数据进行聚类分析"

            # 标准化特征
            X = self.scaler.fit_transform(user_features)

            # PCA降维
            pca = PCA(n_components=2)
            X_pca = pca.fit_transform(X)

            # KMeans聚类
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            labels = kmeans.fit_predict(X)

            # 评估聚类效果
            if len(set(labels)) > 1:
                silhouette_avg = silhouette_score(X, labels)
                self.logger.info(f"用户行为聚类评分 (Silhouette): {silhouette_avg:.4f}")

            # 创建结果字典
            clusters = {}
            for i, label in enumerate(labels):
                if label not in clusters:
                    clusters[int(label)] = []
                clusters[int(label)].append(valid_keywords[i])

            # 聚类特征中心分析
            centers = kmeans.cluster_centers_
            center_analysis = self._analyze_user_clusters(centers)

            # 生成可视化图表
            visualization_path = self._create_visualization(X_pca, labels, valid_keywords, title="用户行为聚类分析")

            # 关闭数据库连接
            cursor.close()
            conn.close()

            return {
                'clusters': clusters,
                'cluster_analysis': center_analysis,
                'visualization': visualization_path
            }, "用户行为聚类分析完成"

        except Exception as e:
            self.logger.error(f"用户行为聚类失败: {str(e)}")
            return None, f"聚类失败: {str(e)}"

    def _create_visualization(self, X_pca, labels, keywords, title="关键词聚类分析"):
        """创建聚类可视化并保存为HTML文件"""
        try:
            # 调用新的pyecharts可视化方法
            html_path = self.plot_clusters(X_pca, labels, keywords)
            return html_path
        except Exception as e:
            self.logger.error(f"创建聚类可视化失败: {str(e)}")
            return None

    def _get_feature_importance(self, pca):
        """获取特征重要性"""
        try:
            feature_names = [
                "平均指数", "最大指数", "最小指数", "波动性",
                "主要年龄组占比", "男性占比", "区域集中度", "相关词数量"
            ]

            # 计算特征对主成分的贡献
            components = pca.components_
            importance = np.abs(components[0]) + np.abs(components[1])  # 前两个主成分的综合重要性

            # 归一化重要性
            importance = importance / np.sum(importance)

            # 创建特征重要性字典
            importance_dict = {}
            for i, feature in enumerate(feature_names):
                if i < len(importance):
                    importance_dict[feature] = float(importance[i])

            return importance_dict

        except Exception as e:
            self.logger.error(f"计算特征重要性失败: {str(e)}")
            return {}

    def _analyze_user_clusters(self, centers):
        """分析用户聚类中心，生成人群画像描述"""
        try:
            feature_names = [
                "19岁以下", "20-29岁", "30-39岁", "40-49岁", "50岁以上",
                "男性比例", "女性比例", "兴趣多样性"
            ]

            age_groups = ["19岁以下", "20-29岁", "30-39岁", "40-49岁", "50岁以上"]

            analysis = {}

            for i, center in enumerate(centers):
                cluster_analysis = {}

                # 找出主要年龄段
                age_values = center[:5]
                max_age_idx = np.argmax(age_values)
                main_age = age_groups[max_age_idx]

                # 性别偏好
                gender_ratio = center[5] / (center[6] + 0.001)  # 避免除零
                if gender_ratio > 1.2:
                    gender_pref = "男性为主"
                elif gender_ratio < 0.8:
                    gender_pref = "女性为主"
                else:
                    gender_pref = "男女均衡"

                # 兴趣特征
                interest_diversity = "高" if center[7] > 0.6 else ("中" if center[7] > 0.3 else "低")

                # 生成更丰富的分析描述
                cluster_analysis = {
                    "age_group": main_age,
                    "gender_pref": gender_pref,
                    "interest_diversity": interest_diversity,
                    "人群画像": f"以{main_age}的{gender_pref}用户为主，兴趣多样性{interest_diversity}"
                }

                # 添加额外的特点描述，确保每个聚类都有差异化描述
                if max_age_idx <= 1:  # 年轻人群（19岁以下或20-29岁）
                    if gender_ratio > 1.2:  # 男性为主
                        cluster_analysis["特点"] = "年轻男性群体，可能对科技、游戏等领域更感兴趣"
                    else:  # 女性为主或均衡
                        cluster_analysis["特点"] = "年轻用户群体，可能对时尚、社交媒体等领域更感兴趣"
                elif max_age_idx == 2:  # 30-39岁
                    if gender_ratio > 1.2:  # 男性为主
                        cluster_analysis["特点"] = "中年男性群体，可能对职业发展、投资理财等领域更感兴趣"
                    else:  # 女性为主或均衡
                        cluster_analysis["特点"] = "中年家庭群体，可能对家居、育儿等领域更感兴趣"
                else:  # 40岁以上
                    if gender_ratio > 1.2:  # 男性为主
                        cluster_analysis["特点"] = "成熟男性群体，可能对健康、投资等领域更感兴趣"
                    else:  # 女性为主或均衡
                        cluster_analysis["特点"] = "成熟用户群体，可能对健康、休闲等领域更感兴趣"

                analysis[i] = cluster_analysis

            return analysis

        except Exception as e:
            self.logger.error(f"分析用户聚类失败: {str(e)}")
            return {}

    def generate_cluster_insights(self, cluster_results):
        """根据聚类结果生成洞察"""
        insights = []

        try:
            clusters = cluster_results.get('clusters', {})

            # 基本聚类统计
            cluster_sizes = {k: len(v) for k, v in clusters.items()}
            total_items = sum(cluster_sizes.values())

            # 生成洞察
            insights.append(f"总共发现{len(clusters)}个不同的聚类组")

            # 分析最大的聚类组
            if cluster_sizes:
                largest_cluster = max(cluster_sizes, key=cluster_sizes.get)
                largest_size = cluster_sizes[largest_cluster]
                largest_percent = (largest_size / total_items) * 100

                insights.append(
                    f"最大的聚类组(聚类{largest_cluster})包含{largest_size}个项目，占总数的{largest_percent:.1f}%")

                # 如果是关键词聚类，分析特征重要性
                if 'feature_importance' in cluster_results:
                    importance = cluster_results['feature_importance']
                    if importance:
                        # 找出最重要的特征
                        top_features = sorted(importance.items(), key=lambda x: x[1], reverse=True)[:3]
                        features_text = "、".join([f"{name}({value:.1%})" for name, value in top_features])
                        insights.append(f"聚类中最重要的特征是: {features_text}")

                # 如果是用户行为聚类，添加人群画像分析
                if 'cluster_analysis' in cluster_results:
                    analysis = cluster_results['cluster_analysis']
                    # 为每个聚类组添加一条不同的洞察
                    for cluster_id, cluster_info in analysis.items():
                        # 确保不同聚类有不同的特征描述，避免重复
                        if 'age_group' in cluster_info:
                            insights.append(
                                f"聚类{cluster_id}的人群画像: 以{cluster_info.get('age_group', '')}为主，{cluster_info.get('gender_pref', '')}，兴趣多样性{cluster_info.get('interest_diversity', '')}")
                        else:
                            insights.append(f"聚类{cluster_id}的人群画像: {cluster_info.get('人群画像', '')}")

            return insights

        except Exception as e:
            self.logger.error(f"生成聚类洞察失败: {str(e)}")
            return ["聚类洞察生成失败"]

    def generate_sample_data(self, save_to_db=False):
        """
        生成示例数据用于测试聚类功能

        Args:
            save_to_db: 是否将示例数据保存到数据库

        Returns:
            bool: 是否成功生成示例数据
        """
        try:
            import random
            from datetime import datetime, timedelta

            # 示例关键词
            sample_keywords = [
                "老年健康", "养老中心", "老年医疗", "养老保险", "老年活动",
                "老年人饮食", "老年人运动", "中老年服装", "老年大学", "老年旅游",
                "医疗保健", "老年护理", "老年心理", "老年住宅", "老年人保健品",
                "老年人智能手机", "老年人理财", "退休生活", "养老院", "居家养老"
            ]

            if save_to_db:
                # 连接数据库
                conn = db_utils.get_connection()
                if not conn:
                    self.logger.error("数据库连接失败")
                    return False

                cursor = conn.cursor()

                # 先清空现有表数据
                try:
                    cursor.execute("TRUNCATE TABLE baidu_index_trends")
                    cursor.execute("TRUNCATE TABLE crowd_age_data")
                    cursor.execute("TRUNCATE TABLE crowd_gender_data")
                    cursor.execute("TRUNCATE TABLE crowd_region_data")
                    cursor.execute("TRUNCATE TABLE human_request_data")
                    self.logger.info("已清空原有测试数据表")
                except Exception as e:
                    self.logger.warning(f"清空表失败，将尝试继续: {str(e)}")

                # 创建必要的表(如果不存在)
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

                # 为每个关键词生成数据
                today = datetime.now().date()
                for keyword in sample_keywords:
                    # 趋势数据 - 最近30天
                    base_value = random.randint(1000, 10000)
                    for i in range(30):
                        date = today - timedelta(days=i)
                        index_value = base_value + random.randint(-500, 500)
                        cursor.execute("""
                            INSERT INTO baidu_index_trends (date, index_value, area, keyword)
                            VALUES (%s, %s, %s, %s)
                        """, (date, index_value, '全国', keyword))

                    # 年龄数据
                    age_groups = ["19岁以下", "20-29岁", "30-39岁", "40-49岁", "50岁以上"]
                    age_distribution = [random.random() for _ in range(5)]
                    total = sum(age_distribution)
                    age_distribution = [value / total for value in age_distribution]

                    for i, age_group in enumerate(age_groups):
                        cursor.execute("""
                            INSERT INTO crowd_age_data (typeId, name, tgi, rate, keyword, date)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (1, age_group, 100 + random.randint(-20, 50), age_distribution[i], keyword, today))

                    # 性别数据
                    male_rate = random.random() * 0.7 + 0.3  # 30% - 100%
                    female_rate = 1 - male_rate

                    cursor.execute("""
                        INSERT INTO crowd_gender_data (typeId, name, tgi, rate, keyword, date)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (1, "男", 100 + random.randint(-20, 50), male_rate, keyword, today))

                    cursor.execute("""
                        INSERT INTO crowd_gender_data (typeId, name, tgi, rate, keyword, date)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (1, "女", 100 + random.randint(-20, 50), female_rate, keyword, today))

                    # 区域数据
                    regions = ["北京", "上海", "广州", "深圳", "成都", "杭州", "武汉", "西安", "南京", "重庆"]
                    for region in random.sample(regions, 5):
                        value = random.randint(10, 200)  # 使用整数值
                        cursor.execute("""
                            INSERT INTO crowd_region_data (province, value, keyword, date)
                            VALUES (%s, %s, %s, %s)
                        """, (region, value, keyword, today))

                    # 需求图谱数据
                    related_terms = [
                        f"{keyword}推荐", f"{keyword}评价", f"{keyword}价格",
                        f"{keyword}品牌", f"{keyword}服务", f"最好的{keyword}",
                        f"{keyword}对比", f"{keyword}优惠", f"{keyword}政策",
                        f"{keyword}方案"
                    ]

                    for term in related_terms[:random.randint(3, 8)]:
                        search_count = random.randint(100, 2000)
                        ratio = round(random.random() * 10, 2)  # 0-10%
                        sim = round(random.random() * 100, 2)  # 0-100%
                        cursor.execute("""
                            INSERT INTO human_request_data (word, pv, ratio, sim, keyword, date)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (term, search_count, ratio, sim, keyword, today))

                # 提交更改
                conn.commit()
                cursor.close()
                conn.close()

                self.logger.info(f"成功生成示例数据并保存到数据库，共{len(sample_keywords)}个关键词")
                return True
            else:
                # 仅返回示例数据而不保存到数据库
                return True

        except Exception as e:
            self.logger.error(f"生成示例数据失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def run_clustering(self, parameters):
        """
        根据参数执行聚类分析

        Args:
            parameters (dict): 包含聚类参数的字典，必须包含cluster_type、algorithm和n_clusters

        Returns:
            dict: 聚类结果
        """
        try:
            cluster_type = parameters.get("cluster_type", "keywords")
            algorithm = parameters.get("algorithm", "kmeans")
            n_clusters = parameters.get("n_clusters", 3)
            keywords = parameters.get("keywords", None)

            # 记录
            self.logger.info(f"开始执行{cluster_type}聚类，算法:{algorithm}，聚类数量:{n_clusters}")

            # 根据类型选择聚类方法
            if cluster_type.lower() == "keywords":
                result, message = self.keyword_clustering(
                    keywords=keywords,
                    n_clusters=n_clusters,
                    method=algorithm
                )
            elif cluster_type.lower() == "users":
                result, message = self.user_behavior_clustering(n_clusters=n_clusters)
            else:
                return {"error": f"未知的聚类类型: {cluster_type}"}

            if not result:
                return {"error": message}

            # 添加原始参数信息到结果
            result["parameters"] = parameters

            # 添加简化的点数据用于直接绘图
            if "visualization" in result:
                plot_data = {}
                try:
                    import matplotlib.pyplot as plt
                    import numpy as np
                    from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
                    from matplotlib.figure import Figure
                    import io
                    import base64
                    from PIL import Image
                    import os

                    # 创建保存路径
                    plot_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data',
                                            'clusters')
                    if not os.path.exists(plot_dir):
                        os.makedirs(plot_dir)

                    # 获取图片路径
                    plot_path = result["visualization"]

                    # 如果图片存在，处理图片数据
                    if os.path.exists(plot_path):
                        # 打开图片
                        img = Image.open(plot_path)

                        # 创建缩略图 (可选)
                        thumb_path = os.path.join(plot_dir, os.path.basename(plot_path).replace('.png', '_thumb.png'))
                        img_copy = img.copy()
                        img_copy.thumbnail((400, 300))
                        img_copy.save(thumb_path)

                        # 更新结果
                        result["plot_thumb"] = thumb_path

                    # 添加简化数据用于绘图
                    clusters = result.get('clusters', {})
                    plot_data = {}
                    for cluster_id, items in clusters.items():
                        plot_data[cluster_id] = []
                        # 为每个聚类组生成随机点位置(仅用于测试)
                        center_x = np.random.uniform(-5, 5)
                        center_y = np.random.uniform(-5, 5)
                        for item in items:
                            x = center_x + np.random.normal(0, 1)
                            y = center_y + np.random.normal(0, 1)
                            plot_data[cluster_id].append((x, y))

                    result["plot_data"] = plot_data

                except Exception as e:
                    self.logger.error(f"处理图表数据时出错: {str(e)}")

            return result

        except Exception as e:
            self.logger.error(f"执行聚类分析时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}

    def plot_clusters(self, data, labels, keywords=None):
        """
        可视化聚类结果

        Args:
            data: 降维后的数据点
            labels: 聚类标签
            keywords: 对应每个点的关键词列表

        Returns:
            html_path: 生成的HTML文件路径
        """
        # 创建临时HTML文件
        temp_dir = tempfile.gettempdir()
        html_path = os.path.join(temp_dir, 'cluster_visualization.html')

        # 获取唯一的标签
        unique_labels = np.unique(labels)
        n_clusters = len(unique_labels)

        # 为每个簇创建不同颜色
        colors = [
            "#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd",
            "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"
        ]

        # 创建散点图实例
        scatter = Scatter()

        # 为每个簇添加数据系列
        for i, label in enumerate(unique_labels):
            cluster_points = data[labels == label]

            # 准备数据
            x_data = cluster_points[:, 0].tolist()
            y_data = cluster_points[:, 1].tolist()

            # 准备点的名称（如果提供了关键词）
            data_points = []
            for j, (x, y) in enumerate(zip(x_data, y_data)):
                point_index = np.where((data[:, 0] == x) & (data[:, 1] == y))[0][0]
                if keywords is not None and point_index < len(keywords):
                    name = keywords[point_index]
                else:
                    name = f"Point {point_index}"
                data_points.append([x, y, name])

            # 添加系列
            scatter.add_xaxis([d[0] for d in data_points])
            scatter.add_yaxis(
                f"簇 {label}",
                [list(d[1:]) for d in data_points],
                symbol_size=15,
                label_opts=opts.LabelOpts(is_show=True, formatter="{@[1]}"),
                itemstyle_opts=opts.ItemStyleOpts(color=colors[i % len(colors)])
            )

        # 设置图表选项
        scatter.set_global_opts(
            title_opts=opts.TitleOpts(title="聚类分析结果可视化"),
            xaxis_opts=opts.AxisOpts(
                type_="value",
                name="维度1",
                splitline_opts=opts.SplitLineOpts(is_show=True)
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name="维度2",
                splitline_opts=opts.SplitLineOpts(is_show=True)
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="item",
                formatter="{c}"
            ),
            legend_opts=opts.LegendOpts(is_show=True),
        )

        # 生成HTML文件
        scatter.render(html_path)
        logging.info(f"聚类可视化保存为: {html_path}")

        return html_path