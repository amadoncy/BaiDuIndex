import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor

import datetime
import logging
from utils import db_utils

class DataPredictionUtils:
    def __init__(self):
        self.scaler = MinMaxScaler(feature_range=(0, 1))
        self.rf_model = RandomForestRegressor(n_estimators=100, random_state=42)

    def create_sequences(self, data, seq_length):
        """创建时间序列数据"""
        sequences = []
        targets = []
        for i in range(len(data) - seq_length):
            sequences.append(data[i:(i + seq_length)])
            targets.append(data[i + seq_length])
        return np.array(sequences), np.array(targets)

    def predict_trend(self, keyword, days_to_predict=30):
        """预测趋势数据"""
        try:
            # 获取历史数据
            connection = db_utils.get_connection()
            cursor = connection.cursor()
            
            query = """
            SELECT date, index_value 
            FROM baidu_index_trends 
            WHERE keyword = %s 
            ORDER BY date
            """
            cursor.execute(query, (keyword,))
            results = cursor.fetchall()
            
            if not results:
                return None, "没有找到历史数据"

            # 转换为DataFrame
            df = pd.DataFrame(results, columns=['date', 'value'])
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')

            # 创建特征
            df['day_of_week'] = df.index.dayofweek
            df['month'] = df.index.month
            df['day'] = df.index.day
            
            # 使用过去7天的值作为特征
            for i in range(1, 8):
                df[f'lag_{i}'] = df['value'].shift(i)
            
            # 删除包含NaN的行
            df = df.dropna()

            # 准备特征和目标
            X = df[['day_of_week', 'month', 'day'] + [f'lag_{i}' for i in range(1, 8)]].values
            y = df['value'].values

            # 训练模型
            self.rf_model.fit(X, y)

            # 生成未来日期
            last_date = df.index[-1]
            future_dates = pd.date_range(start=last_date + datetime.timedelta(days=1), 
                                       periods=days_to_predict, freq='D')
            
            # 准备预测
            predictions = []
            current_values = list(df['value'].values[-7:])  # 最后7天的值

            for future_date in future_dates:
                features = [
                    future_date.dayofweek,
                    future_date.month,
                    future_date.day
                ] + current_values[-7:]  # 使用最近7天的值

                pred = self.rf_model.predict([features])[0]
                predictions.append(pred)
                current_values.append(pred)  # 更新最近的值

            # 创建预测结果DataFrame
            pred_df = pd.DataFrame(predictions, index=future_dates, columns=['predicted_value'])
            pred_df['predicted_value'] = pred_df['predicted_value'].astype(float)
            
            return pred_df, "预测成功"

        except Exception as e:
            logging.error(f"趋势预测失败: {str(e)}")
            return None, f"预测失败: {str(e)}"
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def predict_age_distribution(self, keyword):
        """预测年龄分布变化"""
        try:
            connection = db_utils.get_connection()
            cursor = connection.cursor()
            
            query = """
            SELECT date, name, rate 
            FROM crowd_age_data 
            WHERE keyword = %s 
            ORDER BY date
            """
            cursor.execute(query, (keyword,))
            results = cursor.fetchall()
            
            if not results:
                return None, "没有找到历史数据"

            # 转换为DataFrame
            df = pd.DataFrame(results, columns=['date', 'age_group', 'rate'])
            df['date'] = pd.to_datetime(df['date'])
            
            # 数据透视表
            pivot_df = df.pivot(index='date', columns='age_group', values='rate')
            
            # 对每个年龄组进行预测
            predictions = {}
            for age_group in pivot_df.columns:
                values = pivot_df[age_group].values.reshape(-1, 1)
                
                # 创建时间特征
                dates = pivot_df.index
                X = np.column_stack([
                    dates.dayofweek.values.reshape(-1, 1),
                    dates.month.values.reshape(-1, 1),
                    dates.day.values.reshape(-1, 1),
                    np.arange(len(dates)).reshape(-1, 1)  # 添加趋势特征
                ])
                
                # 训练随机森林模型
                self.rf_model.fit(X, values.ravel())
                
                # 预测下一个时间点
                next_date = dates[-1] + datetime.timedelta(days=1)
                next_point = np.array([[
                    next_date.dayofweek,
                    next_date.month,
                    next_date.day,
                    len(dates)
                ]])
                pred = self.rf_model.predict(next_point)
                predictions[age_group] = pred[0]

            # 确保预测值的总和为100%
            total = sum(predictions.values())
            if total != 0:
                predictions = {str(k): float(v/total*100) for k, v in predictions.items()}
            else:
                predictions = {str(k): 0.0 for k in predictions.keys()}

            return predictions, "预测成功"

        except Exception as e:
            logging.error(f"年龄分布预测失败: {str(e)}")
            return None, f"预测失败: {str(e)}"
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def predict_gender_distribution(self, keyword):
        """预测性别分布变化"""
        try:
            connection = db_utils.get_connection()
            cursor = connection.cursor()
            
            query = """
            SELECT date, name, rate 
            FROM crowd_gender_data 
            WHERE keyword = %s 
            ORDER BY date
            """
            cursor.execute(query, (keyword,))
            results = cursor.fetchall()
            
            if not results:
                return None, "没有找到历史数据"

            # 转换为DataFrame
            df = pd.DataFrame(results, columns=['date', 'gender', 'rate'])
            df['date'] = pd.to_datetime(df['date'])
            
            # 数据透视表
            pivot_df = df.pivot(index='date', columns='gender', values='rate')
            
            # 对每个性别进行预测
            predictions = {}
            for gender in pivot_df.columns:
                values = pivot_df[gender].values.reshape(-1, 1)
                
                # 创建时间特征
                dates = pivot_df.index
                X = np.column_stack([
                    dates.dayofweek.values.reshape(-1, 1),
                    dates.month.values.reshape(-1, 1),
                    dates.day.values.reshape(-1, 1),
                    np.arange(len(dates)).reshape(-1, 1)  # 添加趋势特征
                ])
                
                # 训练随机森林模型
                self.rf_model.fit(X, values.ravel())
                
                # 预测下一个时间点
                next_date = dates[-1] + datetime.timedelta(days=1)
                next_point = np.array([[
                    next_date.dayofweek,
                    next_date.month,
                    next_date.day,
                    len(dates)
                ]])
                pred = self.rf_model.predict(next_point)
                predictions[gender] = pred[0]

            # 确保预测值的总和为100%
            total = sum(predictions.values())
            if total != 0:
                predictions = {str(k): float(v/total*100) for k, v in predictions.items()}
            else:
                predictions = {str(k): 0.0 for k in predictions.keys()}

            return predictions, "预测成功"

        except Exception as e:
            logging.error(f"性别分布预测失败: {str(e)}")
            return None, f"预测失败: {str(e)}"
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def predict_region_distribution(self, keyword):
        """预测地域分布变化"""
        try:
            connection = db_utils.get_connection()
            cursor = connection.cursor()
            
            query = """
            SELECT date, province, value 
            FROM crowd_region_data 
            WHERE keyword = %s 
            ORDER BY date
            """
            cursor.execute(query, (keyword,))
            results = cursor.fetchall()
            
            if not results:
                return None, "没有找到历史数据"

            # 转换为DataFrame
            df = pd.DataFrame(results, columns=['date', 'province', 'value'])
            df['date'] = pd.to_datetime(df['date'])
            
            # 数据透视表
            pivot_df = df.pivot(index='date', columns='province', values='value')
            
            # 对每个省份进行预测
            predictions = {}
            for province in pivot_df.columns:
                values = pivot_df[province].values.reshape(-1, 1)
                
                # 创建时间特征
                dates = pivot_df.index
                X = np.column_stack([
                    dates.dayofweek.values.reshape(-1, 1),
                    dates.month.values.reshape(-1, 1),
                    dates.day.values.reshape(-1, 1),
                    np.arange(len(dates)).reshape(-1, 1)  # 添加趋势特征
                ])
                
                # 训练随机森林模型
                self.rf_model.fit(X, values.ravel())
                
                # 预测下一个时间点
                next_date = dates[-1] + datetime.timedelta(days=1)
                next_point = np.array([[
                    next_date.dayofweek,
                    next_date.month,
                    next_date.day,
                    len(dates)
                ]])
                pred = self.rf_model.predict(next_point)
                predictions[province] = pred[0]

            # 确保预测值都是浮点数
            predictions = {str(k): float(v) for k, v in predictions.items()}

            return predictions, "预测成功"

        except Exception as e:
            logging.error(f"地域分布预测失败: {str(e)}")
            return None, f"预测失败: {str(e)}"
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def predict_interest_distribution(self, keyword):
        """预测兴趣分布变化"""
        try:
            connection = db_utils.get_connection()
            cursor = connection.cursor()
            
            query = """
            SELECT data_date, category, name, value 
            FROM crowd_interest_data 
            WHERE keyword = %s 
            ORDER BY data_date
            """
            cursor.execute(query, (keyword,))
            results = cursor.fetchall()
            
            if not results:
                return None, "没有找到历史数据"

            # 转换为DataFrame
            df = pd.DataFrame(results, columns=['date', 'category', 'interest', 'value'])
            df['date'] = pd.to_datetime(df['date'])
            
            # 合并category和interest作为标识
            df['category_interest'] = df['category'] + '-' + df['interest']
            
            # 数据透视表
            pivot_df = df.pivot(index='date', 
                              columns='category_interest', 
                              values='value')
            
            # 对每个兴趣类别进行预测
            predictions = {}
            for category_interest in pivot_df.columns:
                values = pivot_df[category_interest].fillna(0).values.reshape(-1, 1)
                
                # 创建时间特征
                dates = pivot_df.index
                X = np.column_stack([
                    dates.dayofweek.values.reshape(-1, 1),
                    dates.month.values.reshape(-1, 1),
                    dates.day.values.reshape(-1, 1),
                    np.arange(len(dates)).reshape(-1, 1)  # 添加趋势特征
                ])
                
                # 训练随机森林模型
                self.rf_model.fit(X, values.ravel())
                
                # 预测下一个时间点
                next_date = dates[-1] + datetime.timedelta(days=1)
                next_point = np.array([[
                    next_date.dayofweek,
                    next_date.month,
                    next_date.day,
                    len(dates)
                ]])
                pred = self.rf_model.predict(next_point)
                predictions[category_interest] = pred[0]

            # 确保预测值都是浮点数
            predictions = {str(k): float(v) for k, v in predictions.items()}

            return predictions, "预测成功"

        except Exception as e:
            logging.error(f"兴趣分布预测失败: {str(e)}")
            return None, f"预测失败: {str(e)}"
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def predict_demand_keywords(self, keyword):
        """预测需求关键词变化"""
        try:
            connection = db_utils.get_connection()
            cursor = connection.cursor()
            
            query = """
            SELECT date, word, pv 
            FROM human_request_data 
            WHERE keyword = %s 
            ORDER BY date
            """
            cursor.execute(query, (keyword,))
            results = cursor.fetchall()
            
            if not results:
                return None, "没有找到历史数据"

            # 转换为DataFrame
            df = pd.DataFrame(results, columns=['date', 'word', 'pv'])
            df['date'] = pd.to_datetime(df['date'])
            
            # 处理重复数据：对于同一天同一个词的数据，取最大PV值
            df = df.groupby(['date', 'word'])['pv'].max().reset_index()
            
            # 数据透视表
            pivot_df = df.pivot(index='date', columns='word', values='pv')
            pivot_df = pivot_df.fillna(0)  # 填充缺失值
            
            # 对每个关键词进行预测
            predictions = {}
            for word in pivot_df.columns:
                values = pivot_df[word].values.reshape(-1, 1)
                
                # 创建时间特征
                dates = pivot_df.index
                X = np.column_stack([
                    dates.dayofweek.values.reshape(-1, 1),
                    dates.month.values.reshape(-1, 1),
                    dates.day.values.reshape(-1, 1),
                    np.arange(len(dates)).reshape(-1, 1)  # 添加趋势特征
                ])
                
                # 训练随机森林模型
                self.rf_model.fit(X, values.ravel())
                
                # 预测下一个时间点
                next_date = dates[-1] + datetime.timedelta(days=1)
                next_point = np.array([[
                    next_date.dayofweek,
                    next_date.month,
                    next_date.day,
                    len(dates)
                ]])
                pred = self.rf_model.predict(next_point)
                predictions[word] = pred[0]

            # 确保预测值都是浮点数，并且只保留前10个最高的预测值
            predictions = {str(k): float(v) for k, v in predictions.items()}
            sorted_predictions = dict(sorted(predictions.items(), 
                                          key=lambda x: x[1], 
                                          reverse=True)[:10])

            return sorted_predictions, "预测成功"

        except Exception as e:
            logging.error(f"需求关键词预测失败: {str(e)}")
            return None, f"预测失败: {str(e)}"
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def generate_prediction_insights(self, keyword):
        """生成预测建议报告"""
        try:
            insights = []
            
            # 1. 趋势预测分析
            trend_pred, trend_msg = self.predict_trend(keyword)
            if trend_pred is not None and not trend_pred.empty:
                current_value = trend_pred['predicted_value'].iloc[0]
                future_value = trend_pred['predicted_value'].iloc[-1]
                trend_percentage = ((future_value - current_value) / current_value) * 100
                trend_direction = "上升" if trend_percentage > 0 else "下降"
                insights.append(f"• 未来30天搜索趋势预计将{trend_direction}，变化幅度约为{abs(trend_percentage):.1f}%")
            
            # 2. 年龄分布分析
            age_pred, age_msg = self.predict_age_distribution(keyword)
            if age_pred is not None and len(age_pred) > 0:
                max_age_group = max(age_pred.items(), key=lambda x: x[1])
                insights.append(f"• 主要用户群体集中在{max_age_group[0]}年龄段，占比约{max_age_group[1]:.1f}%")
            
            # 3. 性别分布分析
            gender_pred, gender_msg = self.predict_gender_distribution(keyword)
            if gender_pred is not None and len(gender_pred) > 0:
                max_gender = max(gender_pred.items(), key=lambda x: x[1])
                insights.append(f"• 用户性别分布以{max_gender[0]}性为主，占比约{max_gender[1]:.1f}%")
            
            # 4. 地域分布分析
            region_pred, region_msg = self.predict_region_distribution(keyword)
            if region_pred is not None and len(region_pred) > 0:
                top_regions = sorted(region_pred.items(), key=lambda x: x[1], reverse=True)[:3]
                regions_str = "、".join([f"{region}" for region, _ in top_regions])
                insights.append(f"• 用户主要分布在{regions_str}等地区")
            
            # 5. 兴趣分布分析
            interest_pred, interest_msg = self.predict_interest_distribution(keyword)
            if interest_pred is not None and len(interest_pred) > 0:
                top_interests = sorted(interest_pred.items(), key=lambda x: x[1], reverse=True)[:3]
                interests_str = "\n  ".join([f"- {interest.split('-')[1]}（{interest.split('-')[0]}）" for interest, _ in top_interests])
                insights.append(f"• 用户兴趣主要集中在：\n  {interests_str}")
            
            # 6. 需求关键词分析
            demand_pred, demand_msg = self.predict_demand_keywords(keyword)
            if demand_pred is not None and len(demand_pred) > 0:
                top_keyword = list(demand_pred.items())[0]
                related_keywords = "、".join(list(demand_pred.keys())[1:4])
                insights.append(f"• 建议重点关注\"{top_keyword[0]}\"相关内容的发展")
                insights.append(f"• 其他值得关注的相关词：{related_keywords}")
            
            # 7. 生成综合建议
            insights.append("\n综合建议：")
            if (trend_pred is not None and not trend_pred.empty and
                age_pred is not None and len(age_pred) > 0 and
                gender_pred is not None and len(gender_pred) > 0 and
                region_pred is not None and len(region_pred) > 0 and
                interest_pred is not None and len(interest_pred) > 0 and
                demand_pred is not None and len(demand_pred) > 0):
                
                top_region = top_regions[0][0] if region_pred else "主要地区"
                top_age = max_age_group[0] if age_pred else "目标年龄段"
                top_interest = top_interests[0][0].split('-')[1] if interest_pred else "相关领域"
                
                insights.append(
                    f"根据预测结果，建议在{top_region}地区重点发展{top_age}的{top_interest}相关业务。"
                    f"可以围绕\"{top_keyword[0]}\"展开营销活动，并针对{max_gender[0]}性用户群体进行精准投放。"
                )
            
            return "\n".join(insights), "预测建议生成成功"
            
        except Exception as e:
            logging.error(f"预测建议生成失败: {str(e)}")
            return None, f"预测建议生成失败: {str(e)}" 