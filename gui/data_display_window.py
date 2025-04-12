from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QPushButton, QTabWidget, QMessageBox, QTextEdit)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib
matplotlib.use('Qt5Agg')
plt.style.use('dark_background')
# 设置中文字体
matplotlib.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 设置默认字体为微软雅黑
matplotlib.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
from utils.data_prediction_utils import DataPredictionUtils
import logging

class DataDisplayWindow(QWidget):
    def __init__(self, username=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("百度指数 - 数据分析与预测")
        self.username = username
        self.prediction_utils = DataPredictionUtils()
        self.init_ui()
        
        # 加载关键词列表
        self.load_keywords()

    def init_ui(self):
        """初始化界面"""
        # 创建主布局
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # 创建标题
        title_label = QLabel("数据展示与预测")
        title_label.setFont(QFont("Microsoft YaHei", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: white;
                padding: 10px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
            }
        """)
        layout.addWidget(title_label)

        # 创建控制面板
        control_layout = QHBoxLayout()
        
        # 关键词选择
        keyword_label = QLabel("关键词:")
        keyword_label.setStyleSheet("color: white;")
        self.keyword_combo = QComboBox()
        self.keyword_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 5px;
                color: white;
                min-width: 150px;
            }
        """)

        # 预测按钮
        self.predict_btn = QPushButton("开始预测")
        self.predict_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 20px;
                background: rgba(33, 150, 243, 0.8);
                border: none;
                border-radius: 5px;
                color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(33, 150, 243, 1);
            }
        """)
        self.predict_btn.clicked.connect(self.start_prediction)

        control_layout.addWidget(keyword_label)
        control_layout.addWidget(self.keyword_combo)
        control_layout.addWidget(self.predict_btn)
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        # 创建标签页
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
            }
            QTabWidget::pane {
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                padding: 10px;
            }
            QTabBar::tab {
                background: rgba(255, 255, 255, 0.1);
                color: white;
                padding: 8px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
            }
            QTabBar::tab:selected {
                background: rgba(33, 150, 243, 0.8);
            }
        """)
        
        # 添加各个标签页
        self.tab_widget.addTab(self.create_trend_tab(), "趋势预测")
        self.tab_widget.addTab(self.create_age_tab(), "年龄分布")
        self.tab_widget.addTab(self.create_gender_tab(), "性别分布")
        self.tab_widget.addTab(self.create_region_tab(), "地域分布")
        self.tab_widget.addTab(self.create_interest_tab(), "兴趣分布")
        self.tab_widget.addTab(self.create_demand_tab(), "需求图谱")
        self.tab_widget.addTab(self.create_insights_tab(), "预测建议")
        
        layout.addWidget(self.tab_widget)
        
        self.setLayout(layout)

    def create_trend_tab(self):
        """创建趋势预测标签页"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 创建Figure和Canvas
        fig = Figure(figsize=(10, 6), facecolor='#1a237e')
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        
        # 保存Figure和Canvas的引用
        self.趋势预测_figure = fig
        self.趋势预测_canvas = canvas
        
        tab.setLayout(layout)
        return tab

    def create_age_tab(self):
        """创建年龄分布标签页"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 创建Figure和Canvas
        fig = Figure(figsize=(10, 6), facecolor='#1a237e')
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        
        # 保存Figure和Canvas的引用
        self.年龄分布预测_figure = fig
        self.年龄分布预测_canvas = canvas
        
        tab.setLayout(layout)
        return tab

    def create_gender_tab(self):
        """创建性别分布标签页"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 创建Figure和Canvas
        fig = Figure(figsize=(10, 6), facecolor='#1a237e')
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        
        # 保存Figure和Canvas的引用
        self.性别分布预测_figure = fig
        self.性别分布预测_canvas = canvas
        
        tab.setLayout(layout)
        return tab

    def create_region_tab(self):
        """创建地域分布标签页"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 创建Figure和Canvas
        fig = Figure(figsize=(10, 6), facecolor='#1a237e')
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        
        # 保存Figure和Canvas的引用
        self.地域分布预测_figure = fig
        self.地域分布预测_canvas = canvas
        
        tab.setLayout(layout)
        return tab

    def create_interest_tab(self):
        """创建兴趣分布标签页"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 创建Figure和Canvas
        fig = Figure(figsize=(10, 6), facecolor='#1a237e')
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        
        # 保存Figure和Canvas的引用
        self.兴趣分布预测_figure = fig
        self.兴趣分布预测_canvas = canvas
        
        tab.setLayout(layout)
        return tab

    def create_demand_tab(self):
        """创建需求图谱标签页"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 创建Figure和Canvas
        fig = Figure(figsize=(10, 6), facecolor='#1a237e')
        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        
        # 保存Figure和Canvas的引用
        self.需求关键词预测_figure = fig
        self.需求关键词预测_canvas = canvas
        
        tab.setLayout(layout)
        return tab

    def create_insights_tab(self):
        """创建预测建议标签页"""
        tab = QWidget()
        layout = QVBoxLayout()
        
        # 创建文本显示区域
        self.insights_text = QTextEdit()
        self.insights_text.setReadOnly(True)
        self.insights_text.setStyleSheet("""
            QTextEdit {
                background-color: white;
                color: #333333;
                font-size: 14px;
                line-height: 1.5;
                padding: 10px;
                border: 1px solid #cccccc;
                border-radius: 5px;
            }
        """)
        
        layout.addWidget(self.insights_text)
        tab.setLayout(layout)
        return tab

    def load_keywords(self):
        """加载关键词列表"""
        try:
            # 清空现有的关键词
            self.keyword_combo.clear()

            # 连接数据库
            from utils import db_utils
            connection = db_utils.get_connection()
            cursor = connection.cursor()
            
            # 从所有相关表中获取唯一关键词
            queries = [
                "SELECT DISTINCT keyword FROM baidu_index_trends",
                "SELECT DISTINCT keyword FROM crowd_age_data",
                "SELECT DISTINCT keyword FROM crowd_gender_data",
                "SELECT DISTINCT keyword FROM crowd_region_data",
                "SELECT DISTINCT keyword FROM crowd_interest_data",
                "SELECT DISTINCT keyword FROM human_request_data"
            ]
            
            keywords = set()
            for query in queries:
                try:
                    cursor.execute(query)
                    results = cursor.fetchall()
                    keywords.update(row[0] for row in results)
                    print(f"查询 {query} 结果: {results}")
                except Exception as e:
                    logging.warning(f"执行查询失败: {query}, 错误: {str(e)}")
                    continue
            
            print(f"找到的所有关键词: {keywords}")
            
            # 添加排序后的关键词
            sorted_keywords = sorted(keywords)
            self.keyword_combo.addItems(sorted_keywords)
            
            # 添加提示项（如果列表为空）
            if self.keyword_combo.count() == 0:
                self.keyword_combo.addItem("请先采集数据")
                self.predict_btn.setEnabled(False)
                logging.warning("没有找到任何关键词数据")
                print("没有找到任何关键词数据")
            else:
                self.predict_btn.setEnabled(True)
                logging.info(f"成功加载 {len(sorted_keywords)} 个关键词")
                print(f"成功加载 {len(sorted_keywords)} 个关键词: {sorted_keywords}")
            
            cursor.close()
            connection.close()
            
        except Exception as e:
            logging.error(f"加载关键词失败: {str(e)}")
            print(f"加载关键词失败: {str(e)}")
            self.keyword_combo.clear()
            self.keyword_combo.addItem("数据库连接失败")
            self.predict_btn.setEnabled(False)
            QMessageBox.warning(self, "错误", f"加载关键词失败: {str(e)}")

    def start_prediction(self):
        """开始预测分析"""
        try:
            keyword = self.keyword_combo.currentText()
            if not keyword:
                QMessageBox.warning(self, "错误", "请先选择一个关键词，然后再点击查询按钮")
                return
            
            # 检查下拉列表是否有内容
            if self.keyword_combo.count() == 0:
                QMessageBox.warning(self, "错误", "没有可用的关键词数据。请先采集数据，然后再尝试预测功能。")
                return

            # 预测趋势
            trend_pred, trend_msg = self.prediction_utils.predict_trend(keyword)
            if trend_pred is not None:
                self.show_trend_prediction(trend_pred, keyword)
            else:
                logging.warning(f"趋势预测失败: {trend_msg}")
                QMessageBox.warning(self, "预测提示", f"趋势预测: {trend_msg}")

            # 预测年龄分布
            age_pred, age_msg = self.prediction_utils.predict_age_distribution(keyword)
            if age_pred is not None:
                self.show_age_prediction(age_pred, keyword)
            else:
                logging.warning(f"年龄分布预测失败: {age_msg}")
                QMessageBox.warning(self, "预测提示", f"年龄分布预测: {age_msg}")

            # 预测性别分布
            gender_pred, gender_msg = self.prediction_utils.predict_gender_distribution(keyword)
            if gender_pred is not None:
                self.show_gender_prediction(gender_pred, keyword)
            else:
                logging.warning(f"性别分布预测失败: {gender_msg}")
                QMessageBox.warning(self, "预测提示", f"性别分布预测: {gender_msg}")

            # 预测地域分布
            region_pred, region_msg = self.prediction_utils.predict_region_distribution(keyword)
            if region_pred is not None:
                self.show_region_prediction(region_pred, keyword)
            else:
                logging.warning(f"地域分布预测失败: {region_msg}")
                QMessageBox.warning(self, "预测提示", f"地域分布预测: {region_msg}")

            # 预测兴趣分布
            interest_pred, interest_msg = self.prediction_utils.predict_interest_distribution(keyword)
            if interest_pred is not None:
                self.show_interest_prediction(interest_pred, keyword)
            else:
                logging.warning(f"兴趣分布预测失败: {interest_msg}")
                QMessageBox.warning(self, "预测提示", f"兴趣分布预测: {interest_msg}")

            # 预测需求关键词
            demand_pred, demand_msg = self.prediction_utils.predict_demand_keywords(keyword)
            if demand_pred is not None:
                self.show_demand_prediction(demand_pred, keyword)
            else:
                logging.warning(f"需求关键词预测失败: {demand_msg}")
                QMessageBox.warning(self, "预测提示", f"需求关键词预测: {demand_msg}")

            # 更新预测建议
            insights, msg = self.prediction_utils.generate_prediction_insights(keyword)
            if insights:
                self.insights_text.setPlainText(insights)
            else:
                self.insights_text.setPlainText(f"无法生成预测建议: {msg}")

            QMessageBox.information(self, "成功", "预测分析完成")

        except Exception as e:
            logging.error(f"预测分析失败: {str(e)}")
            QMessageBox.warning(self, "错误", f"预测分析失败: {str(e)}")

    def show_trend_prediction(self, pred_df, keyword):
        """显示趋势预测结果"""
        try:
            fig = self.趋势预测_figure
            fig.clear()
            ax = fig.add_subplot(111)
            
            # 确保数据是正确的类型
            dates = pd.to_datetime(pred_df.index)
            values = pred_df['predicted_value'].astype(float)
            
            # 绘制趋势线
            ax.plot(dates, values, color='#2196F3', linewidth=2, marker='o')
            
            # 设置标题和标签
            ax.set_title(f"{keyword} - 未来30天趋势预测", 
                         color='white', pad=20, fontsize=14,
                         fontproperties='Microsoft YaHei')
            ax.set_xlabel("日期", color='white',
                         fontproperties='Microsoft YaHei')
            ax.set_ylabel("预测值", color='white',
                         fontproperties='Microsoft YaHei')
            
            # 设置刻度标签颜色和字体
            ax.tick_params(colors='white')
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontproperties('Microsoft YaHei')
            
            # 旋转x轴标签
            plt.setp(ax.get_xticklabels(), rotation=45)
            
            # 添加网格
            ax.grid(True, linestyle='--', alpha=0.3)
            
            # 调整布局
            fig.tight_layout()
            
            # 刷新画布
            self.趋势预测_canvas.draw()
        except Exception as e:
            logging.error(f"显示趋势预测结果失败: {str(e)}")
            raise

    def show_age_prediction(self, predictions, keyword):
        """显示年龄分布预测结果"""
        try:
            fig = self.年龄分布预测_figure
            fig.clear()
            ax = fig.add_subplot(111)
            
            # 确保数据是正确的类型
            predictions = {str(k): float(v) for k, v in predictions.items()}
            ages = list(predictions.keys())
            values = list(predictions.values())
            
            # 创建柱状图
            bars = ax.bar(ages, values, color='#2196F3')
            
            # 在柱子上添加数值标签
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                        f'{height:.1f}%',
                        ha='center', va='bottom', color='white',
                        fontproperties='Microsoft YaHei')
            
            # 设置标题和标签
            ax.set_title(f"{keyword} - 年龄分布预测", 
                         color='white', pad=20, fontsize=14,
                         fontproperties='Microsoft YaHei')
            ax.set_xlabel("年龄段", color='white',
                         fontproperties='Microsoft YaHei')
            ax.set_ylabel("比例 (%)", color='white',
                         fontproperties='Microsoft YaHei')
            
            # 设置刻度标签颜色和字体
            ax.tick_params(colors='white')
            for label in ax.get_xticklabels() + ax.get_yticklabels():
                label.set_fontproperties('Microsoft YaHei')
            
            # 添加网格
            ax.grid(True, linestyle='--', alpha=0.3)
            
            # 调整布局
            fig.tight_layout()
            
            # 刷新画布
            self.年龄分布预测_canvas.draw()
        except Exception as e:
            logging.error(f"显示年龄分布预测结果失败: {str(e)}")
            raise

    def show_gender_prediction(self, predictions, keyword):
        """显示性别分布预测结果"""
        try:
            fig = self.性别分布预测_figure
            fig.clear()
            ax = fig.add_subplot(111)
            
            # 确保数据是正确的类型
            predictions = {str(k): float(v) for k, v in predictions.items()}
            labels = list(predictions.keys())
            sizes = list(predictions.values())
            
            # 创建饼图
            wedges, texts, autotexts = ax.pie(sizes, labels=labels, 
                                             autopct='%1.1f%%',
                                             colors=['#2196F3', '#F44336'])
            
            # 设置标题
            ax.set_title(f"{keyword} - 性别分布预测", 
                         color='white', pad=20, fontsize=14,
                         fontproperties='Microsoft YaHei')
            
            # 设置文本颜色和字体
            plt.setp(texts, color='white', fontproperties='Microsoft YaHei')
            plt.setp(autotexts, color='white', fontproperties='Microsoft YaHei')
            
            # 调整布局
            fig.tight_layout()
            
            # 刷新画布
            self.性别分布预测_canvas.draw()
        except Exception as e:
            logging.error(f"显示性别分布预测结果失败: {str(e)}")
            raise

    def show_region_prediction(self, predictions, keyword):
        """显示地域分布预测结果"""
        try:
            fig = self.地域分布预测_figure
            fig.clear()
            ax = fig.add_subplot(111)
            
            # 确保数据是正确的类型
            predictions = {str(k): float(v) for k, v in predictions.items()}
            
            # 对数据进行排序
            sorted_data = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
            regions = [x[0] for x in sorted_data[:10]]  # 只显示前10个地区
            values = [x[1] for x in sorted_data[:10]]
            
            # 创建水平柱状图
            bars = ax.barh(regions, values, color='#2196F3')
            
            # 在柱子上添加数值标签
            for bar in bars:
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2.,
                        f'{width:.1f}',
                        ha='left', va='center', color='white',
                        fontproperties='Microsoft YaHei')
            
            # 设置标题和标签
            ax.set_title(f"{keyword} - 地域分布预测 (Top 10)", 
                         color='white', pad=20, fontsize=14,
                         fontproperties='Microsoft YaHei')
            ax.set_xlabel("预测值", color='white',
                         fontproperties='Microsoft YaHei')
            
            # 设置刻度标签颜色和字体
            ax.tick_params(colors='white')
            for label in ax.get_yticklabels():
                label.set_fontproperties('Microsoft YaHei')
            
            # 添加网格
            ax.grid(True, linestyle='--', alpha=0.3)
            
            # 调整布局
            fig.tight_layout()
            
            # 刷新画布
            self.地域分布预测_canvas.draw()
        except Exception as e:
            logging.error(f"显示地域分布预测结果失败: {str(e)}")
            raise

    def show_interest_prediction(self, predictions, keyword):
        """显示兴趣分布预测结果"""
        try:
            fig = self.兴趣分布预测_figure
            fig.clear()
            ax = fig.add_subplot(111)
            
            # 确保数据是正确的类型
            predictions = {str(k): float(v) for k, v in predictions.items()}
            
            # 对数据进行排序
            sorted_data = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
            interests = [x[0] for x in sorted_data[:10]]  # 只显示前10个兴趣
            values = [x[1] for x in sorted_data[:10]]
            
            # 创建水平柱状图
            bars = ax.barh(interests, values, color='#2196F3')
            
            # 在柱子上添加数值标签
            for bar in bars:
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2.,
                        f'{width:.1f}',
                        ha='left', va='center', color='white',
                        fontproperties='Microsoft YaHei')
            
            # 设置标题和标签
            ax.set_title(f"{keyword} - 兴趣分布预测 (Top 10)", 
                         color='white', pad=20, fontsize=14,
                         fontproperties='Microsoft YaHei')
            ax.set_xlabel("预测值", color='white',
                         fontproperties='Microsoft YaHei')
            
            # 设置刻度标签颜色和字体
            ax.tick_params(colors='white')
            for label in ax.get_yticklabels():
                label.set_fontproperties('Microsoft YaHei')
            
            # 添加网格
            ax.grid(True, linestyle='--', alpha=0.3)
            
            # 调整布局
            fig.tight_layout()
            
            # 刷新画布
            self.兴趣分布预测_canvas.draw()
        except Exception as e:
            logging.error(f"显示兴趣分布预测结果失败: {str(e)}")
            raise

    def show_demand_prediction(self, predictions, keyword):
        """显示需求关键词预测结果"""
        try:
            fig = self.需求关键词预测_figure
            fig.clear()
            ax = fig.add_subplot(111)
            
            # 确保数据是正确的类型
            predictions = {str(k): float(v) for k, v in predictions.items()}
            
            # 对数据进行排序
            sorted_data = sorted(predictions.items(), key=lambda x: x[1], reverse=True)
            words = [x[0] for x in sorted_data[:10]]  # 只显示前10个关键词
            values = [x[1] for x in sorted_data[:10]]
            
            # 创建水平柱状图
            bars = ax.barh(words, values, color='#2196F3')
            
            # 在柱子上添加数值标签
            for bar in bars:
                width = bar.get_width()
                ax.text(width, bar.get_y() + bar.get_height()/2.,
                        f'{width:.1f}',
                        ha='left', va='center', color='white',
                        fontproperties='Microsoft YaHei')
            
            # 设置标题和标签
            ax.set_title(f"{keyword} - 需求关键词预测 (Top 10)", 
                         color='white', pad=20, fontsize=14,
                         fontproperties='Microsoft YaHei')
            ax.set_xlabel("预测值", color='white',
                         fontproperties='Microsoft YaHei')
            
            # 设置刻度标签颜色和字体
            ax.tick_params(colors='white')
            for label in ax.get_yticklabels():
                label.set_fontproperties('Microsoft YaHei')
            
            # 添加网格
            ax.grid(True, linestyle='--', alpha=0.3)
            
            # 调整布局
            fig.tight_layout()
            
            # 刷新画布
            self.需求关键词预测_canvas.draw()
        except Exception as e:
            logging.error(f"显示需求关键词预测结果失败: {str(e)}")
            raise 