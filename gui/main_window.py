from PyQt5.QtWidgets import (QMainWindow, QWidget, QLabel,
                             QVBoxLayout, QHBoxLayout, QPushButton,
                             QMessageBox, QListWidget, QStackedWidget,
                             QListWidgetItem, QFrame, QComboBox, QSpinBox,
                             QLineEdit, QProgressBar, QTextEdit, QTabWidget,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QGroupBox, QRadioButton, QButtonGroup, QCheckBox,
                             QProgressDialog, QFileDialog, QInputDialog)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QSize, QThread, pyqtSignal, QUrl
from PyQt5.QtGui import QFont, QColor, QPalette, QLinearGradient, QPainter, QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings
import os
import logging
from datetime import datetime, timedelta
from utils.get_local_weather_utils import get_weather_info
import requests
import json
from utils.get_trend_utils import get_trend_utils, select_area
from config.city_codes import get_all_regions, get_region_provinces, get_province_cities
from pyecharts import options as opts
from pyecharts.charts import Line, Bar, Pie, Map, Graph, Page
from utils import db_utils
from gui.data_display_window import DataDisplayWindow
import random
import time
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.figure import Figure
from wordcloud import WordCloud
from utils.db_utils import DatabaseConnection
import threading
from utils.get_huamn_requestion_utils import get_human_request_data
from utils.get_index_cookie_utils import get_index_cookie, get_login_user_info
from gui.user_management_window import UserManagementWindow


class DataCollectionThread(QThread):
    """数据采集线程类"""
    progress_signal = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)

    def __init__(self, collection_type, username, keyword=None, area_code=0, area_name="全国"):
        super().__init__()
        self.collection_type = collection_type
        self.username = username
        self.keyword = keyword
        self.area_code = area_code
        self.area_name = area_name
        self._is_running = True
        self.base_dir = os.path.dirname(os.path.dirname(__file__))

    def stop(self):
        self._is_running = False

    def run(self):
        try:
            if not self._is_running:
                return

            if self.collection_type == "trend":
                # 趋势数据采集
                result = get_trend_utils(self.username, self.keyword, self.area_code, self.area_name)
                if result and self._is_running:
                    self.finished_signal.emit(True, "趋势数据采集完成")
                else:
                    self.finished_signal.emit(False, "趋势数据采集失败")

            elif self.collection_type == "portrait":
                # 人群画像数据采集
                self.progress_signal.emit("正在采集人群画像数据...")
                try:
                    # 调用人群画像数据采集函数
                    from utils.get_crowd_portrait_utils import get_crowd_portrait_data
                    success = get_crowd_portrait_data(self.keyword, self.base_dir)

                    if success and self._is_running:
                        self.progress_signal.emit("人群画像数据采集完成")
                        self.finished_signal.emit(True, "人群画像数据采集完成")
                    else:
                        self.finished_signal.emit(False, "人群画像数据采集失败")
                except Exception as e:
                    self.finished_signal.emit(False, f"人群画像数据采集出错: {str(e)}")

            elif self.collection_type == "demand":
                # 需求图谱数据采集
                self.progress_signal.emit("正在采集需求图谱数据...")
                try:
                    success = get_human_request_data(self.keyword, self.username)

                    if success and self._is_running:
                        self.progress_signal.emit("需求图谱数据采集完成")
                        self.finished_signal.emit(True, "需求图谱数据采集完成")
                    else:
                        self.finished_signal.emit(False, "需求图谱数据采集失败")
                except Exception as e:
                    self.finished_signal.emit(False, f"需求图谱数据采集出错: {str(e)}")

        except Exception as e:
            if self._is_running:
                self.finished_signal.emit(False, f"错误: {str(e)}")


class KeywordDataCollectionThread(threading.Thread):
    """多线程关键词数据采集类"""
    _semaphore = threading.Semaphore(5)  # 类级别的信号量，限制最大线程数为5

    def __init__(self, keyword, username, thread_id):
        super().__init__()
        self.keyword = keyword
        self.username = username
        self.thread_id = thread_id
        self.result = None
        self.base_dir = os.path.dirname(os.path.dirname(__file__))

    def run(self):
        try:
            with KeywordDataCollectionThread._semaphore:
                logging.info(f"线程 {self.thread_id} 开始获取关键词 '{self.keyword}' 的数据")

                # 获取cookies
                cookies = get_index_cookie(self.username)
                if not cookies:
                    logging.error(f"线程 {self.thread_id} 获取cookies失败")
                    return

                # 获取需求图谱数据
                success = get_human_request_data(self.keyword, self.username)
                if not success:
                    logging.error(f"线程 {self.thread_id} 获取需求图谱数据失败")
                    return

                # 获取趋势数据
                trend_data = get_trend_utils(self.username, self.keyword)
                if not trend_data:
                    logging.error(f"线程 {self.thread_id} 获取趋势数据失败")
                    return

                # 获取人群画像数据
                from utils.get_crowd_portrait_utils import get_crowd_portrait_data
                portrait_success = get_crowd_portrait_data(self.keyword, self.base_dir)
                if not portrait_success:
                    logging.error(f"线程 {self.thread_id} 获取人群画像数据失败")
                    return

                self.result = True
                logging.info(f"线程 {self.thread_id} 完成数据获取")

        except Exception as e:
            logging.error(f"线程 {self.thread_id} 执行出错: {str(e)}")
            self.result = False


class WelcomeWindow(QMainWindow):
    # 定义主题样式
    THEME_STYLES = {
        "深蓝主题": {
            "gradient": """
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #1a237e,
                    stop: 0.4 #0d47a1,
                    stop: 1 #01579b
                );
            """,
            "button_style": """
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.2);
                    border: 2px solid white;
                    color: white;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.3);
                }
            """,
            "list_style": """
                QListWidget::item:selected {
                    background-color: rgba(255, 255, 255, 0.3);
                    color: white;
                }
            """,
            "text_color": "white",
            "bg_opacity": "rgba(255, 255, 255, 0.1)",
            "border_color": "rgba(255, 255, 255, 0.1)"
        },
        "暗夜主题": {
            "gradient": """
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #2c3e50,
                    stop: 0.4 #34495e,
                    stop: 1 #2c3e50
                );
            """,
            "button_style": """
                QPushButton {
                    background-color: rgba(52, 152, 219, 0.2);
                    border: 2px solid #3498db;
                    color: white;
                }
                QPushButton:hover {
                    background-color: rgba(52, 152, 219, 0.3);
                }
            """,
            "list_style": """
                QListWidget::item:selected {
                    background-color: rgba(52, 152, 219, 0.3);
                    color: white;
                }
            """,
            "text_color": "white",
            "bg_opacity": "rgba(255, 255, 255, 0.1)",
            "border_color": "rgba(52, 152, 219, 0.1)"
        },
        "浅色主题": {
            "gradient": """
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #e0f7fa,
                    stop: 0.4 #b2ebf2,
                    stop: 1 #80deea
                );
            """,
            "button_style": """
                QPushButton {
                    background-color: rgba(0, 151, 167, 0.2);
                    border: 2px solid #00838f;
                    color: #006064;
                }
                QPushButton:hover {
                    background-color: rgba(0, 151, 167, 0.3);
                }
            """,
            "list_style": """
                QListWidget::item {
                    color: #006064;
                }
                QListWidget::item:selected {
                    background-color: rgba(0, 151, 167, 0.3);
                    color: #006064;
                }
            """,
            "text_color": "#006064",
            "bg_opacity": "rgba(0, 151, 167, 0.1)",
            "border_color": "rgba(0, 151, 167, 0.1)"
        }
    }

    def __init__(self, username):
        super().__init__()
        self.username = username
        self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cache')
        # 确保缓存目录存在
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        self.init_ui()
        # 创建定时器，每30分钟更新一次天气
        self.weather_timer = QTimer(self)
        self.weather_timer.timeout.connect(self.update_weather)
        self.weather_timer.start(30 * 60 * 1000)  # 30分钟
        # 立即更新一次天气
        self.update_weather()
        self.collection_thread = None

    def update_weather(self):
        """更新天气信息"""
        try:
            weather_info = get_weather_info()
            if weather_info:
                # 获取城市名称
                city_name = self.get_city_name(weather_info['location'])
                if city_name:
                    self.weather_label.setText(
                        f"{city_name}\n当前温度: {weather_info['temp']}°C\n天气：{weather_info['text']}")
                else:
                    self.weather_label.setText(f"温度: {weather_info['temp']}°C\n天气：{weather_info['text']}")
        except Exception as e:
            logging.error(f"更新天气信息失败: {str(e)}")

    def get_city_name(self, location_id):
        """根据城市ID获取城市名称"""
        try:
            key = 'f527040e397d4f95b39d4518a057702d'
            city_api = f'https://geoapi.qweather.com/v2/city/lookup?location={location_id}&key={key}'
            response = requests.get(city_api)
            response.raise_for_status()
            city_data = response.json()

            if city_data.get('code') == '200' and city_data.get('location'):
                return city_data['location'][0]['name']
            return None
        except Exception as e:
            logging.error(f"获取城市名称失败: {str(e)}")
            return None

    def init_ui(self):
        try:
            # 设置窗口基本属性
            self.setWindowTitle("养老需求分析系统")
            self.setMinimumSize(1200, 800)
            self.setStyleSheet("""
                QMainWindow {
                    background: qlineargradient(
                        x1: 0, y1: 0, x2: 1, y2: 1,
                        stop: 0 #1a237e,
                        stop: 0.4 #0d47a1,
                        stop: 1 #01579b
                    );
                }
                QLabel {
                    color: white;
                }
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.2);
                    border: 2px solid white;
                    border-radius: 10px;
                    color: white;
                    padding: 10px 20px;
                    font-size: 14px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.3);
                    border-color: #E3F2FD;
                }
                QPushButton:pressed {
                    background-color: rgba(255, 255, 255, 0.1);
                }
                QPushButton#logout_btn {
                    background-color: rgba(244, 67, 54, 0.2);
                    border: 2px solid #f44336;
                    border-radius: 8px;
                    color: white;
                    font-weight: bold;
                    padding: 8px 20px;
                }
                QPushButton#logout_btn:hover {
                    background-color: rgba(244, 67, 54, 0.3);
                    border-color: #ff5252;
                }
                QPushButton#logout_btn:pressed {
                    background-color: rgba(244, 67, 54, 0.4);
                }
                QListWidget {
                    background-color: rgba(255, 255, 255, 0.1);
                    border: none;
                    border-radius: 10px;
                    padding: 10px;
                }
                QListWidget::item {
                    color: white;
                    padding: 15px;
                    margin: 5px 0;
                    border-radius: 5px;
                    background-color: rgba(255, 255, 255, 0.1);
                }
                QListWidget::item:selected {
                    background-color: rgba(255, 255, 255, 0.3);
                    color: white;
                }
                QStackedWidget {
                    background-color: rgba(255, 255, 255, 0.1);
                    border-radius: 10px;
                    padding: 20px;
                }
                QMessageBox {
                    background-color: #f0f0f0;
                }
                QMessageBox QLabel {
                    color: #333333;
                    font-size: 14px;
                    font-family: "Microsoft YaHei";
                }
                QMessageBox QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    border-radius: 5px;
                    padding: 8px 16px;
                    font-size: 14px;
                    min-width: 80px;
                }
                QMessageBox QPushButton:hover {
                    background-color: #45a049;
                }
                QFrame#left_panel {
                    background-color: rgba(0, 0, 0, 0.2);
                    border-right: 2px solid rgba(255, 255, 255, 0.1);
                }
                QFrame#right_panel {
                    background-color: rgba(255, 255, 255, 0.05);
                }
                QLabel#weather_label {
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 10px;
                    padding: 15px;
                    font-size: 14px;
                    line-height: 1.5;
                }
            """)

            # 创建中央部件
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            # 创建主布局
            main_layout = QHBoxLayout(central_widget)
            main_layout.setContentsMargins(0, 0, 0, 0)
            main_layout.setSpacing(0)

            # 创建左侧面板
            left_panel = QFrame()
            left_panel.setObjectName("left_panel")
            left_panel.setFixedWidth(280)
            left_layout = QVBoxLayout(left_panel)
            left_layout.setContentsMargins(20, 20, 20, 20)
            left_layout.setSpacing(20)

            # 添加天气信息
            self.weather_label = QLabel()
            self.weather_label.setObjectName("weather_label")
            self.weather_label.setAlignment(Qt.AlignCenter)
            left_layout.addWidget(self.weather_label)

            # 添加系统标题
            title_label = QLabel("养老需求分析系统")
            title_label.setFont(QFont("Microsoft YaHei", 20, QFont.Bold))
            title_label.setAlignment(Qt.AlignCenter)
            title_label.setStyleSheet("""
                QLabel {
                    color: white;
                    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
                    padding: 10px;
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 10px;
                }
            """)
            left_layout.addWidget(title_label)

            # 创建功能列表
            self.function_list = QListWidget()
            self.function_list.setFont(QFont("Microsoft YaHei", 12))

            # 添加功能项
            functions = [
                {"title": "数据采集", "description": "开始收集养老需求数据"},
                {"title": "数据分析", "description": "分析已收集的数据"},
                {"title": "数据展示", "description": "展示分析结果"},
                {"title": "聚类分析", "description": "关键词聚类与分析"},
                {"title": "数据报告", "description": "生成综合分析报告"},
                {"title": "系统设置", "description": "调整系统配置"}
            ]
            if self.is_admin():
                functions.append({"title": "用户管理", "description": "管理系统用户"})
            self.function_list.clear()
            for function in functions:
                item = QListWidgetItem(f"{function['title']}\n{function['description']}")
                item.setData(Qt.UserRole, function['title'])
                self.function_list.addItem(item)

            left_layout.addWidget(self.function_list)

            # 添加退出登录按钮到底部
            logout_container = QFrame()
            logout_container.setStyleSheet("""
                QFrame {
                    background: rgba(255, 255, 255, 0.1);
                    border-radius: 10px;
                    padding: 10px;
                }
            """)
            logout_layout = QVBoxLayout(logout_container)
            logout_layout.setContentsMargins(10, 10, 10, 10)

            logout_btn = QPushButton("退出登录")
            logout_btn.setObjectName("logout_btn")
            logout_btn.setFixedHeight(45)
            logout_btn.setFont(QFont("Microsoft YaHei", 12))
            logout_btn.clicked.connect(self.handle_logout)
            logout_layout.addWidget(logout_btn)

            left_layout.addWidget(logout_container)

            # 创建右侧面板
            right_panel = QFrame()
            right_panel.setObjectName("right_panel")
            right_layout = QVBoxLayout(right_panel)
            right_layout.setContentsMargins(30, 30, 30, 30)

            # 创建右侧内容区域
            self.content_stack = QStackedWidget()

            # 添加各个功能页面
            self.content_stack.addWidget(self.create_data_collection_page())
            self.content_stack.addWidget(self.create_data_analysis_page())
            self.content_stack.addWidget(self.create_data_display_page())
            self.content_stack.addWidget(self.create_cluster_analysis_page())
            self.content_stack.addWidget(self.create_export_page())
            self.content_stack.addWidget(self.create_settings_page())

            # 连接功能列表的选择信号
            self.function_list.currentRowChanged.connect(self.content_stack.setCurrentIndex)
            self.function_list.currentRowChanged.connect(self.switch_page)

            right_layout.addWidget(self.content_stack)

            # 将左右面板添加到主布局
            main_layout.addWidget(left_panel)
            main_layout.addWidget(right_panel)

            # 设置窗口图标
            icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'logo.png')
            if os.path.exists(icon_path):
                self.setWindowIcon(QIcon(icon_path))

            # 启动动画效果
            self.start_animations()

        except Exception as e:
            logging.error(f"初始化界面时发生错误: {str(e)}")
            QMessageBox.critical(self, "错误", f"初始化界面时发生错误：{str(e)}")
            self.close()

    def is_admin(self):
        db = DatabaseConnection()
        cursor = db.connection.cursor()
        cursor.execute("SELECT role FROM users WHERE username = %s", (self.username,))
        result = cursor.fetchone()
        return result and result[0] == "admin"

    def handle_logout(self):
        """处理退出登录"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Question)
        msg.setWindowTitle('确认退出')
        msg.setText('确定要退出登录吗？')
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.No)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #f0f0f0;
            }
            QMessageBox QLabel {
                color: #333333;
                font-size: 14px;
                font-family: "Microsoft YaHei";
            }
            QMessageBox QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 16px;
                font-size: 14px;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #45a049;
            }
        """)

        if msg.exec_() == QMessageBox.Yes:
            self.close()
            from gui.loginwindow import LoginWindow
            self.login_window = LoginWindow()
            self.login_window.show()

    def create_data_collection_page(self):
        """创建数据采集页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)

        # 创建标题
        title_label = QLabel("数据采集")
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

        # 创建关键词输入框
        keyword_layout = QHBoxLayout()
        keyword_label = QLabel("关键词:")
        keyword_label.setStyleSheet("color: white;")
        self.keyword_input = QLineEdit()
        self.keyword_input.setPlaceholderText("请输入要查询的关键词")
        self.keyword_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 5px;
                color: white;
            }
            QLineEdit:focus {
                border: 2px solid rgba(255, 255, 255, 0.5);
            }
        """)
        keyword_layout.addWidget(keyword_label)
        keyword_layout.addWidget(self.keyword_input)
        layout.addLayout(keyword_layout)

        # 创建地区选择部分
        region_layout = QHBoxLayout()

        # 区域选择
        region_label = QLabel("地区:")
        region_label.setStyleSheet("color: white;")
        self.region_combo = QComboBox()
        self.region_combo.addItem("全国")
        regions = get_all_regions()
        self.region_combo.addItems(regions)
        self.region_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 5px;
                color: white;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(resources/down_arrow.png);
                width: 12px;
                height: 12px;
            }
        """)

        # 省份选择
        self.province_combo = QComboBox()
        self.province_combo.setEnabled(False)
        self.province_combo.setStyleSheet(self.region_combo.styleSheet())

        # 城市选择
        self.city_combo = QComboBox()
        self.city_combo.setEnabled(False)
        self.city_combo.setStyleSheet(self.region_combo.styleSheet())

        region_layout.addWidget(region_label)
        region_layout.addWidget(self.region_combo)
        region_layout.addWidget(self.province_combo)
        region_layout.addWidget(self.city_combo)
        layout.addLayout(region_layout)

        # 连接信号
        self.region_combo.currentIndexChanged.connect(self.on_region_changed)
        self.province_combo.currentIndexChanged.connect(self.on_province_changed)

        # 创建按钮组
        button_layout = QHBoxLayout()

        # 趋势数据按钮
        self.trend_btn = QPushButton("趋势数据采集")
        self.trend_btn.setToolTip("收集关键词随时间变化的趋势数据")
        self.trend_btn.clicked.connect(lambda: self.select_collection_type("trend"))

        # 人群画像按钮
        self.portrait_btn = QPushButton("人群画像采集")
        self.portrait_btn.setToolTip("收集用户群体特征数据")
        self.portrait_btn.clicked.connect(lambda: self.select_collection_type("portrait"))

        # 需求图谱按钮
        self.demand_btn = QPushButton("需求图谱采集")
        self.demand_btn.setToolTip("收集用户需求关联数据")
        self.demand_btn.clicked.connect(lambda: self.select_collection_type("demand"))

        # 设置按钮样式
        for btn in [self.trend_btn, self.portrait_btn, self.demand_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    padding: 10px;
                    background: rgba(33, 150, 243, 0.8);
                    border: none;
                    border-radius: 5px;
                    color: white;
                    font-weight: bold;
                    min-width: 150px;
                }
                QPushButton:hover {
                    background: rgba(33, 150, 243, 1);
                }
                QPushButton:pressed {
                    background: rgba(25, 118, 210, 1);
                }
            """)
            button_layout.addWidget(btn)

        layout.addLayout(button_layout)

        # 添加开始采集按钮
        start_button_layout = QHBoxLayout()
        self.start_btn = QPushButton("开始采集")
        self.start_btn.setEnabled(False)  # 初始状态禁用
        self.start_btn.setStyleSheet("""
            QPushButton {
                padding: 15px;
                background: rgba(76, 175, 80, 0.8);
                border: none;
                border-radius: 5px;
                color: white;
                font-weight: bold;
                font-size: 16px;
                min-width: 200px;
            }
            QPushButton:hover {
                background: rgba(76, 175, 80, 1);
            }
            QPushButton:pressed {
                background: rgba(56, 142, 60, 1);
            }
            QPushButton:disabled {
                background: rgba(158, 158, 158, 0.8);
            }
        """)
        self.start_btn.clicked.connect(self.start_collection)
        start_button_layout.addStretch()
        start_button_layout.addWidget(self.start_btn)
        start_button_layout.addStretch()
        layout.addLayout(start_button_layout)

        # 创建进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 5px;
                text-align: center;
                color: white;
            }
            QProgressBar::chunk {
                background-color: rgba(33, 150, 243, 0.8);
            }
        """)
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        # 创建结果显示区域
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("""
            QTextEdit {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 5px;
                color: white;
                padding: 10px;
            }
        """)
        layout.addWidget(self.result_text)

        return page

    def on_region_changed(self):
        """处理区域选择变化"""
        self.province_combo.clear()
        self.city_combo.clear()

        if self.region_combo.currentText() == "全国":
            self.province_combo.setEnabled(False)
            self.city_combo.setEnabled(False)
            return

        self.province_combo.setEnabled(True)
        provinces = get_region_provinces(self.region_combo.currentText())
        self.province_combo.addItems(provinces)

    def on_province_changed(self):
        """处理省份选择变化"""
        self.city_combo.clear()

        if not self.province_combo.currentText():
            self.city_combo.setEnabled(False)
            return

        self.city_combo.setEnabled(True)
        cities = get_province_cities(self.province_combo.currentText())
        self.city_combo.addItems(cities)

    def select_collection_type(self, collection_type):
        """选择数据采集类型"""
        self.current_collection_type = collection_type
        self.start_btn.setEnabled(True)

        # 定义基础样式
        base_style = """
            QPushButton {
                padding: 10px;
                background: rgba(33, 150, 243, 0.8);
                border: none;
                border-radius: 5px;
                color: white;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background: rgba(33, 150, 243, 1);
            }
            QPushButton:pressed {
                background: rgba(25, 118, 210, 1);
            }
        """

        # 定义选中样式
        selected_style = """
            QPushButton {
                padding: 10px;
                background: rgba(33, 150, 243, 1);
                border: 2px solid white;
                border-radius: 5px;
                color: white;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background: rgba(33, 150, 243, 1);
            }
            QPushButton:pressed {
                background: rgba(25, 118, 210, 1);
            }
        """

        # 更新按钮状态
        type_map = {
            "trend": self.trend_btn,
            "portrait": self.portrait_btn,
            "demand": self.demand_btn
        }

        # 重置所有按钮样式
        for btn in type_map.values():
            btn.setStyleSheet(base_style)

        # 设置选中按钮样式
        if collection_type in type_map:
            type_map[collection_type].setStyleSheet(selected_style)

    def start_collection(self):
        """开始数据采集"""
        try:
            if not self.username:
                QMessageBox.warning(self, "错误", "用户未登录")
                return

            if not self.keyword_input.text():
                QMessageBox.warning(self, "错误", "请输入关键词")
                return

            if not hasattr(self, 'current_collection_type'):
                QMessageBox.warning(self, "错误", "请选择采集类型")
                return

            # 获取地区信息
            region = self.region_combo.currentText()
            province = self.province_combo.currentText() if self.province_combo.isEnabled() else None
            city = self.city_combo.currentText() if self.city_combo.isEnabled() else None

            # 获取地区代码
            area_code, area_name = select_area(
                region if region != "全国" else None,
                province,
                city
            )

            # 如果有正在运行的线程，先停止它
            if hasattr(self, 'collection_thread') and self.collection_thread and self.collection_thread.isRunning():
                self.collection_thread.stop()
                self.collection_thread.wait()

            # 创建新的数据采集线程
            self.collection_thread = DataCollectionThread(
                self.current_collection_type,
                self.username,
                self.keyword_input.text(),
                area_code,
                area_name
            )
            self.collection_thread.progress_signal.connect(self.update_progress)
            self.collection_thread.finished_signal.connect(self.collection_finished)

            # 禁用所有按钮
            self.trend_btn.setEnabled(False)
            self.portrait_btn.setEnabled(False)
            self.demand_btn.setEnabled(False)
            self.start_btn.setEnabled(False)

            # 开始采集
            self.progress_bar.setMaximum(0)
            self.progress_bar.show()
            self.result_text.clear()
            self.result_text.append(f"正在采集数据...\n采集类型: {self.get_collection_type_name()}\n地区: {area_name}")
            self.collection_thread.start()

        except Exception as e:
            logging.error(f"启动数据采集时发生错误: {str(e)}")
            QMessageBox.warning(self, "错误", f"启动数据采集失败: {str(e)}")
            self.enable_all_buttons()

    def get_collection_type_name(self):
        """获取采集类型的中文名称"""
        type_names = {
            "trend": "趋势数据",
            "portrait": "人群画像",
            "demand": "需求图谱"
        }
        return type_names.get(self.current_collection_type, "未知类型")

    def collection_finished(self, success, message):
        """采集完成处理"""
        try:
            self.progress_bar.setMaximum(100)
            self.progress_bar.setValue(100 if success else 0)
            self.result_text.append(message)

            # 使用QTimer延迟启用按钮，给界面一些时间处理完成事件
            QTimer.singleShot(100, self.enable_all_buttons)

            # 隐藏进度条
            self.progress_bar.hide()

            if success:
                QMessageBox.information(self, "成功", message)
                # 获取当前采集的关键词
                keyword = self.keyword_input.text()
                print(f"数据采集完成，准备分析关键词: {keyword}")
                # 使用QTimer延迟执行数据分析，避免界面卡顿
                QTimer.singleShot(1000, lambda: self.analyze_data(keyword))
                # 延迟切换到数据分析页面
                QTimer.singleShot(1500, lambda: self.function_list.setCurrentRow(1))
            else:
                QMessageBox.warning(self, "错误", message)

            # 清理线程
            if self.collection_thread:
                self.collection_thread.stop()
                self.collection_thread.wait()
                self.collection_thread = None

        except Exception as e:
            logging.error(f"处理采集完成事件时发生错误: {str(e)}")
            print(f"处理采集完成事件时发生错误: {str(e)}")
            self.enable_all_buttons()

    def enable_all_buttons(self):
        """启用所有按钮"""
        try:
            self.trend_btn.setEnabled(True)
            self.portrait_btn.setEnabled(True)
            self.demand_btn.setEnabled(True)
            self.start_btn.setEnabled(True)
        except Exception as e:
            logging.error(f"启用按钮时发生错误: {str(e)}")

    def update_progress(self, message):
        """更新进度信息"""
        try:
            self.result_text.append(message)
        except Exception as e:
            logging.error(f"更新进度信息时发生错误: {str(e)}")

    def create_data_display_page(self):
        """创建数据展示页面"""
        # 创建数据预测页面并保存用户名
        display_window = DataDisplayWindow(self.username)

        # 当数据分析完成后，通知数据展示页面刷新数据
        def refresh_data():
            display_window.load_keywords()

        # 保证当数据分析完成时，自动刷新数据展示页面
        self.content_stack.currentChanged.connect(lambda index:
                                                  refresh_data() if index == 2 else None)  # 索引2是数据展示页面

        return display_window

    def create_export_page(self):
        """创建数据报告生成页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)

        # 创建标题
        title_label = QLabel("数据报告生成")
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

        # 创建关键词选择区域
        keyword_layout = QHBoxLayout()
        keyword_label = QLabel("选择关键词:")
        keyword_label.setStyleSheet("color: white;")
        self.report_keyword_combo = QComboBox()
        self.report_keyword_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 5px;
                color: white;
                min-width: 200px;
            }
            QComboBox:hover {
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
            QComboBox::drop-down {
                border: 0px;
                width: 30px;
            }
        """)

        # 添加刷新按钮
        self.refresh_button = QPushButton("刷新关键词")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 5px;
                color: white;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
        """)
        self.refresh_button.clicked.connect(self.refresh_report_keywords)

        keyword_layout.addWidget(keyword_label)
        keyword_layout.addWidget(self.report_keyword_combo)
        keyword_layout.addWidget(self.refresh_button)
        layout.addLayout(keyword_layout)

        # 创建报告类型选择
        report_type_layout = QHBoxLayout()
        report_type_label = QLabel("报告类型:")
        report_type_label.setStyleSheet("color: white;")

        self.report_type_group = QButtonGroup()
        report_types = ["完整报告", "趋势分析报告", "人群画像报告", "需求分析报告"]

        report_type_container = QFrame()
        report_type_container.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 5px;
                padding: 5px;
            }
        """)
        report_container_layout = QHBoxLayout(report_type_container)
        report_container_layout.setContentsMargins(10, 5, 10, 5)

        for i, report_type in enumerate(report_types):
            radio = QRadioButton(report_type)
            radio.setStyleSheet("""
                QRadioButton {
                    color: white;
                    spacing: 5px;
                    padding: 5px;
                }
                QRadioButton::indicator {
                    width: 15px;
                    height: 15px;
                    border-radius: 7px;
                }
                QRadioButton::indicator:unchecked {
                    background-color: rgba(255, 255, 255, 0.3);
                    border: 2px solid white;
                }
                QRadioButton::indicator:checked {
                    background-color: #2196F3;
                    border: 2px solid white;
                }
            """)
            self.report_type_group.addButton(radio, i)
            report_container_layout.addWidget(radio)

        # 默认选择第一个
        self.report_type_group.button(0).setChecked(True)

        report_type_layout.addWidget(report_type_label)
        report_type_layout.addWidget(report_type_container)
        report_type_layout.addStretch()
        layout.addLayout(report_type_layout)

        # 报告格式部分移除，只保留HTML格式
        format_info = QLabel("报告格式: HTML网页")
        format_info.setStyleSheet("""
            QLabel {
                color: white;
                padding: 8px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 5px;
            }
        """)
        layout.addWidget(format_info)

        # 添加文件名和保存路径设置
        filename_layout = QHBoxLayout()
        filename_label = QLabel("文件名:")
        filename_label.setStyleSheet("color: white;")
        self.report_filename = QLineEdit()
        self.report_filename.setPlaceholderText("输入报告文件名")
        self.report_filename.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 5px;
                color: white;
            }
            QLineEdit:focus {
                border: 2px solid rgba(255, 255, 255, 0.5);
            }
        """)

        filename_layout.addWidget(filename_label)
        filename_layout.addWidget(self.report_filename)

        path_btn = QPushButton("选择路径")
        path_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 5px;
                color: white;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
                border: 1px solid rgba(255, 255, 255, 0.5);
            }
        """)
        path_btn.clicked.connect(self.select_report_path)

        filename_layout.addWidget(path_btn)
        layout.addLayout(filename_layout)

        # 添加报告路径显示
        self.report_path_label = QLabel("保存路径: ./data/reports/")
        self.report_path_label.setStyleSheet("""
            QLabel {
                color: white;
                padding: 8px;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 5px;
            }
        """)
        layout.addWidget(self.report_path_label)

        # 添加报告摘要和内容选项
        options_container = QFrame()
        options_container.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 10px;
            }
            QCheckBox {
                color: white;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
            }
            QCheckBox::indicator:unchecked {
                background-color: rgba(255, 255, 255, 0.2);
                border: 1px solid white;
            }
            QCheckBox::indicator:checked {
                background-color: #2196F3;
                border: 1px solid white;
            }
        """)

        options_layout = QVBoxLayout(options_container)
        options_layout.setContentsMargins(15, 10, 15, 10)

        options_title = QLabel("报告内容选项")
        options_title.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        options_title.setStyleSheet("color: white;")
        options_layout.addWidget(options_title)

        self.include_summary = QCheckBox("包含报告摘要")
        self.include_summary.setChecked(True)
        self.include_charts = QCheckBox("包含数据图表")
        self.include_charts.setChecked(True)
        self.include_predictions = QCheckBox("包含需求分析")
        self.include_predictions.setChecked(True)
        self.include_recommendations = QCheckBox("包含策略建议")
        self.include_recommendations.setChecked(True)

        options_layout.addWidget(self.include_summary)
        options_layout.addWidget(self.include_charts)
        options_layout.addWidget(self.include_predictions)
        options_layout.addWidget(self.include_recommendations)

        layout.addWidget(options_container)

        # 添加生成报告按钮
        generate_btn = QPushButton("生成报告")
        generate_btn.setMinimumHeight(50)
        generate_btn.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 10px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #42A5F5;
            }
            QPushButton:pressed {
                background-color: #1976D2;
            }
        """)
        generate_btn.clicked.connect(self.generate_report)
        layout.addWidget(generate_btn)

        # 加载已保存的关键词
        self.load_report_keywords()

        return page

    def create_settings_page(self):
        """创建设置页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)

        # 创建标题
        title_label = QLabel("系统设置")
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

        # 创建设置容器
        settings_container = QWidget()
        settings_layout = QVBoxLayout(settings_container)
        settings_layout.setSpacing(20)

        # 添加天气更新间隔设置
        weather_group = QGroupBox("天气更新设置")
        weather_layout = QVBoxLayout(weather_group)

        weather_interval_label = QLabel("更新间隔（分钟）:")
        weather_interval_label.setStyleSheet("color: white;")
        weather_layout.addWidget(weather_interval_label)

        weather_interval_spin = QSpinBox()
        weather_interval_spin.setRange(1, 60)
        weather_interval_spin.setValue(30)
        weather_layout.addWidget(weather_interval_spin)
        weather_group.setLayout(weather_layout)
        settings_layout.addWidget(weather_group)

        # 添加字体大小设置
        font_group = QGroupBox("字体大小设置")
        font_layout = QVBoxLayout(font_group)

        font_size_label = QLabel("字体大小:")
        font_size_label.setStyleSheet("color: white;")
        font_layout.addWidget(font_size_label)

        font_size_spin = QSpinBox()
        font_size_spin.setRange(8, 20)
        font_size_spin.setValue(12)
        font_layout.addWidget(font_size_spin)
        font_group.setLayout(font_layout)
        settings_layout.addWidget(font_group)

        # 添加主题设置
        theme_group = QGroupBox("主题设置")
        theme_layout = QVBoxLayout(theme_group)

        theme_label = QLabel("选择主题:")
        theme_label.setStyleSheet("color: white;")
        theme_layout.addWidget(theme_label)

        theme_combo = QComboBox()
        theme_combo.addItems(["深色主题", "浅色主题"])
        theme_combo.setStyleSheet("""
            QComboBox {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(resources/down_arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        theme_combo.currentTextChanged.connect(self.update_theme)
        theme_layout.addWidget(theme_combo)
        settings_layout.addWidget(theme_group)

        # 添加数据缓存设置
        cache_group = QGroupBox("数据缓存设置")
        cache_layout = QVBoxLayout(cache_group)

        clear_cache_btn = QPushButton("清除缓存")
        clear_cache_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        clear_cache_btn.clicked.connect(self.clear_cache)
        cache_layout.addWidget(clear_cache_btn)

        settings_layout.addWidget(cache_group)

        # 添加团队信息设置
        team_group = QGroupBox("团队信息")
        team_layout = QVBoxLayout(team_group)

        about_btn = QPushButton("查看团队信息")
        about_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
        """)
        about_btn.clicked.connect(self.show_about)
        team_layout.addWidget(about_btn)

        settings_layout.addWidget(team_group)

        layout.addWidget(settings_container)
        layout.addStretch()

        # 加载保存的设置
        self.load_settings()

        return page

    def clear_data_tables(self):
        """清空数据表内容"""
        try:
            # 显示确认对话框
            reply = QMessageBox.question(
                self,
                "确认清空",
                "确定要清空所有数据表吗？此操作不可恢复！\n（area_codes、users、cookies表除外）",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # 连接数据库
                connection = db_utils.get_connection()
                cursor = connection.cursor()

                # 获取所有表名
                cursor.execute("SHOW TABLES")
                tables = [table[0] for table in cursor.fetchall()]

                # 需要保留的表
                protected_tables = ['area_codes', 'users', 'cookies']

                # 清空每个表
                for table in tables:
                    if table not in protected_tables:
                        try:
                            cursor.execute(f"TRUNCATE TABLE {table}")
                            logging.info(f"已清空表: {table}")
                        except Exception as e:
                            logging.error(f"清空表 {table} 失败: {str(e)}")

                # 提交更改
                connection.commit()
                cursor.close()
                connection.close()

                QMessageBox.information(self, "成功", "数据表已清空")
                logging.info("所有数据表已清空")

        except Exception as e:
            logging.error(f"清空数据表失败: {str(e)}")
            QMessageBox.warning(self, "错误", f"清空数据表失败: {str(e)}")

    def show_message(self, title, text):
        """显示统一样式的消息框"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle(title)
        msg.setText(text)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #333333;
                font-size: 14px;
                font-family: "Microsoft YaHei";
                min-width: 200px;
                max-width: 200px;
            }
            QMessageBox QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
                font-size: 13px;
                min-width: 60px;
            }
            QMessageBox QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        msg.exec_()

    def update_weather_interval(self, interval):
        """更新天气更新频率"""
        try:
            # 将文本转换为分钟数
            if interval == "10分钟":
                minutes = 10
            elif interval == "30分钟":
                minutes = 30
            elif interval == "1小时":
                minutes = 60
            else:
                minutes = 120

            # 更新定时器间隔
            self.weather_timer.setInterval(minutes * 60 * 1000)
            self.show_message("设置成功", f"天气更新频率已设置为{interval}")
        except Exception as e:
            logging.error(f"更新天气频率出错: {str(e)}")
            QMessageBox.warning(self, "设置失败", "更新天气更新频率失败")

    def update_font_size(self, size):
        """更新界面字体大小"""
        try:
            # 更新应用字体大小
            self.setStyleSheet(self.styleSheet() + f"\n* {{ font-size: {size}px; }}")
            self.show_message("设置成功", f"界面字体大小已设置为{size}px")
        except Exception as e:
            logging.error(f"更新字体大小失败: {str(e)}")
            QMessageBox.warning(self, "设置失败", "更新字体大小失败")

    def update_theme(self, theme):
        """更新界面主题"""
        try:
            theme_style = self.THEME_STYLES.get(theme)
            if not theme_style:
                raise ValueError(f"未知的主题: {theme}")

            # 构建完整的样式表
            style_sheet = f"""
                QMainWindow {{
                    {theme_style['gradient']}
                }}

                QLabel {{
                    color: {theme_style['text_color']};
                }}

                {theme_style['button_style']}

                QListWidget {{
                    background-color: {theme_style['bg_opacity']};
                    border: none;
                    border-radius: 10px;
                    padding: 10px;
                }}

                QListWidget::item {{
                    color: {theme_style['text_color']};
                    padding: 15px;
                    margin: 5px 0;
                    border-radius: 5px;
                    background-color: {theme_style['bg_opacity']};
                }}

                {theme_style['list_style']}

                QFrame#left_panel {{
                    background-color: {theme_style['bg_opacity']};
                    border-right: 2px solid {theme_style['border_color']};
                }}

                QFrame#right_panel {{
                    background-color: {theme_style['bg_opacity']};
                }}

                QLabel#weather_label {{
                    background: {theme_style['bg_opacity']};
                    border-radius: 10px;
                    padding: 15px;
                    font-size: 14px;
                    line-height: 1.5;
                }}

                QPushButton#logout_btn {{
                    background-color: rgba(244, 67, 54, 0.2);
                    border: 2px solid #f44336;
                    color: {theme_style['text_color']};
                }}

                QPushButton#logout_btn:hover {{
                    background-color: rgba(244, 67, 54, 0.3);
                }}

                QComboBox {{
                    background-color: {theme_style['bg_opacity']};
                    border: 2px solid {theme_style['text_color']};
                    border-radius: 8px;
                    color: {theme_style['text_color']};
                    padding: 8px;
                    min-width: 150px;
                }}

                QSpinBox {{
                    background-color: {theme_style['bg_opacity']};
                    border: 2px solid {theme_style['text_color']};
                    border-radius: 8px;
                    color: {theme_style['text_color']};
                    padding: 8px;
                    min-width: 80px;
                }}
            """

            self.setStyleSheet(style_sheet)
            self.show_message("设置成功", f"界面主题已切换为{theme}")

        except Exception as e:
            logging.error(f"更新主题失败: {str(e)}")
            QMessageBox.warning(self, "设置失败", "更新主题失败")

    def select_report_path(self):
        """选择报告保存路径"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择保存目录", "./data/reports/")
        if dir_path:
            self.report_path_label.setText(f"保存路径: {dir_path}/")

    def load_report_keywords(self):
        """加载可用于生成报告的关键词"""
        try:
            # 连接到数据库并获取已分析的关键词列表
            from utils.db_utils import get_connection
            conn = get_connection()
            cursor = conn.cursor()
            # 使用baidu_index_trends表代替不存在的trend_data表
            cursor.execute("SELECT DISTINCT keyword FROM baidu_index_trends ORDER BY keyword")
            keywords = [row[0] for row in cursor.fetchall()]

            # 如果没有关键词，尝试从其他表获取
            if not keywords:
                cursor.execute("SELECT DISTINCT keyword FROM crowd_region_data ORDER BY keyword")
                keywords = [row[0] for row in cursor.fetchall()]

            # 如果还是没有关键词，再尝试另一个表
            if not keywords:
                cursor.execute("SELECT DISTINCT keyword FROM human_request_data ORDER BY keyword")
                keywords = [row[0] for row in cursor.fetchall()]

            # 如果没有关键词，添加提示选项
            if not keywords:
                self.report_keyword_combo.addItem("暂无可用数据")
            else:
                self.report_keyword_combo.addItems(keywords)

            conn.close()
        except Exception as e:
            logging.error(f"加载报告关键词时出错: {str(e)}")
            self.report_keyword_combo.addItem("加载关键词失败")
            # 避免将错误详情显示在UI上，仅记录到日志文件中
            import traceback
            traceback.print_exc()
            # 添加一些默认关键词以便于测试
            self.report_keyword_combo.clear()
            self.report_keyword_combo.addItems(["老人健康", "养老院", "智能陪护", "健康监测"])

    def generate_report(self):
        """生成数据分析报告"""
        try:
            # 获取关键词并检查有效性
            keyword = self.report_keyword_combo.currentText()

            # 记录关键词内容到日志，帮助调试
            logging.info(f"选择的下拉框关键词: [{keyword}]")

            # 检查关键词是否为空或无效
            if keyword == "暂无可用数据" or keyword == "加载关键词失败" or keyword == "数据库连接失败" or not keyword.strip():
                logging.info("下拉框关键词无效，弹出对话框让用户手动输入")
                # 弹出对话框让用户手动输入
                from PyQt5.QtWidgets import QInputDialog
                input_keyword, ok = QInputDialog.getText(self, "输入关键词",
                                                         "请输入要生成报告的关键词:")
                if ok and input_keyword.strip():
                    keyword = input_keyword.strip()
                    logging.info(f"用户输入的关键词: {keyword}")
                else:
                    # 如果用户取消输入或输入为空，使用默认值
                    keyword = "默认关键词"
                    logging.info("用户未输入关键词，使用默认值")

            # 确保关键词不为None或空字符串
            if not keyword or not keyword.strip():
                keyword = "默认关键词"
                logging.info("关键词为空，使用默认值")

            # 获取报告类型
            report_type_id = self.report_type_group.checkedId()
            report_types = ["完整报告", "趋势分析报告", "人群画像报告", "需求分析报告"]
            report_type = report_types[report_type_id]

            # 确保报告类型不为None或空字符串
            if not report_type or not report_type.strip():
                report_type = "完整报告"
                logging.info("报告类型为空，使用默认值")

            # 报告格式固定为HTML网页
            report_format = "HTML网页"

            # 获取文件名
            filename = self.report_filename.text()
            if not filename:
                # 使用默认文件名
                filename = f"{keyword}_{report_type}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

            # 获取保存路径
            save_path = self.report_path_label.text().replace("保存路径: ", "")

            # 确保保存目录存在
            if not os.path.exists(save_path):
                os.makedirs(save_path)

            # 获取报告内容选项
            include_summary = self.include_summary.isChecked()
            include_charts = self.include_charts.isChecked()
            include_predictions = self.include_predictions.isChecked()
            include_recommendations = self.include_recommendations.isChecked()

            # 显示生成进度
            progress = QProgressDialog("正在生成报告...", "取消", 0, 100, self)
            progress.setWindowTitle("生成报告")
            progress.setWindowModality(Qt.WindowModal)

            # 实际生成报告的代码可以在这里实现
            # 以下模拟报告生成过程
            import time
            for i in range(101):
                progress.setValue(i)
                time.sleep(0.05)  # 模拟处理时间
                if progress.wasCanceled():
                    break
                self.refresh_ui()

            if progress.wasCanceled():
                self.show_message("已取消", "报告生成已取消")
                return

            file_extension = ".html"  # 只使用HTML扩展名
            full_path = os.path.join(save_path, filename + file_extension)

            # 先测试文件写入权限
            test_path = os.path.join(save_path, f"test_{int(time.time())}.txt")
            if not self.create_test_file(test_path):
                self.show_message("错误", f"无法写入文件到指定路径: {save_path}\n请检查目录权限。")
                return

            # 删除测试文件
            try:
                os.remove(test_path)
            except:
                pass  # 忽略删除测试文件的错误

            # 实际创建文件
            try:
                # 创建HTML报告
                success = self.create_simple_text_file(
                    full_path,
                    keyword,
                    report_type,
                    "HTML网页",
                    include_summary=include_summary,
                    include_charts=include_charts,
                    include_predictions=include_predictions,
                    include_recommendations=include_recommendations
                )

                # 验证文件是否成功创建
                if os.path.exists(full_path):
                    from PyQt5.QtWidgets import QPushButton, QMessageBox
                    msg = QMessageBox()
                    msg.setWindowTitle("成功")
                    msg.setText(f"HTML报告已成功生成并保存到:\n{full_path}")
                    msg.setIcon(QMessageBox.Information)

                    # 添加打开文件按钮
                    open_button = QPushButton("打开文件")
                    msg.addButton(open_button, QMessageBox.AcceptRole)
                    msg.addButton("关闭", QMessageBox.RejectRole)

                    # 显示消息框
                    result = msg.exec_()

                    # 如果用户点击了"打开文件"按钮
                    if result == 0:  # AcceptRole (第一个按钮)
                        try:
                            import subprocess
                            if os.name == 'nt':  # Windows
                                os.startfile(full_path)
                            elif os.name == 'posix':  # macOS, Linux
                                subprocess.call(('xdg-open', full_path))
                            logging.info(f"已打开文件: {full_path}")
                        except Exception as open_error:
                            logging.error(f"打开文件失败: {str(open_error)}")
                            self.show_message("提示", f"无法自动打开文件，请手动打开: {full_path}")
                else:
                    self.show_message("警告", f"报告未能保存。\n目标路径: {full_path}\n请检查保存路径的权限或磁盘空间。")
            except Exception as file_error:
                logging.error(f"创建报告文件时出错: {str(file_error)}")
                self.show_message("错误", f"创建报告文件时出错: {str(file_error)}")
                import traceback
                traceback.print_exc()

        except Exception as e:
            logging.error(f"生成报告时出错: {str(e)}")
            self.show_message("错误", f"生成报告时出错: {str(e)}")
            import traceback
            traceback.print_exc()

    def refresh_report_keywords(self):
        """刷新报告关键词列表，从实际存在的表中获取"""
        # 清空当前列表
        self.report_keyword_combo.clear()

        conn = None
        try:
            # 连接到数据库
            from utils.db_utils import get_connection
            conn = get_connection()
            if not conn:
                self.report_keyword_combo.addItem("数据库连接失败")
                return

            cursor = conn.cursor()

            # 检查数据库中所有表
            cursor.execute("SHOW TABLES")
            tables = [table[0] for table in cursor.fetchall()]
            logging.info(f"数据库中的表: {tables}")

            keywords = []
            tables_to_check = ['baidu_index_trends', 'crowd_age_data', 'crowd_gender_data',
                               'crowd_interest_data', 'crowd_region_data', 'human_request_data']

            # 从可能包含关键词的表中收集关键词
            for table in tables_to_check:
                if table in tables:
                    try:
                        cursor.execute(f"SELECT DISTINCT keyword FROM {table} WHERE keyword IS NOT NULL")
                        table_keywords = [row[0] for row in cursor.fetchall()]
                        if table_keywords:
                            keywords.extend(table_keywords)
                            logging.info(f"从{table}表中找到{len(table_keywords)}个关键词")
                    except Exception as e:
                        logging.warning(f"从{table}表获取关键词失败: {str(e)}")

            # 去除重复项并排序
            keywords = list(set(keywords))
            keywords.sort()

            # 添加到下拉框
            if keywords:
                self.report_keyword_combo.addItems(keywords)
                # 添加刷新按钮到报告生成页面
                if hasattr(self, 'refresh_button'):
                    self.refresh_button.setText(f"已加载 {len(keywords)} 个关键词")
            else:
                self.report_keyword_combo.addItem("暂无可用数据")
                if hasattr(self, 'refresh_button'):
                    self.refresh_button.setText("刷新关键词")

        except Exception as e:
            logging.error(f"刷新关键词列表失败: {str(e)}")
            self.report_keyword_combo.addItem("加载关键词失败")
            import traceback
            traceback.print_exc()
        finally:
            if conn:
                conn.close()

    def clear_cache(self):
        """清除数据缓存"""
        try:
            if os.path.exists(self.cache_dir):
                cleared = False
                for file in os.listdir(self.cache_dir):
                    file_path = os.path.join(self.cache_dir, file)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                            cleared = True
                    except Exception as e:
                        logging.error(f"删除缓存文件失败 {file_path}: {str(e)}")

                if cleared:
                    self.show_message("清理成功", "数据缓存已清除")
                else:
                    self.show_message("提示", "缓存目录为空")
            else:
                self.show_message("提示", "缓存目录不存在")
        except Exception as e:
            logging.error(f"清除缓存失败: {str(e)}")
            QMessageBox.warning(self, "清理失败", "清除缓存失败")

    def show_about(self):
        """显示关于系统的信息"""
        about_text = """
        <h2 style='margin-bottom: 10px;'>养老需求分析系统</h2>
        <p style='margin: 5px 0;'>版本：1.0.0</p>
        <p style='margin: 5px 0;'>开发团队：朝阳团队</p>
        <p style='margin: 5px 0;'>联系方式：1402353365@qq.com</p>
        <p style='margin: 5px 0;'>系统简介：本系统用于收集、分析和展示养老需求数据，帮助相关机构更好地了解和满足老年人的需求。</p>
        """

        msg = QMessageBox()
        msg.setWindowTitle("关于系统")
        msg.setTextFormat(Qt.RichText)
        msg.setText(about_text)
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QMessageBox QLabel {
                color: #333333;
                font-size: 14px;
                font-family: "Microsoft YaHei";
                min-width: 300px;
                max-width: 300px;
            }
            QMessageBox QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 5px 15px;
                font-size: 13px;
                min-width: 60px;
            }
            QMessageBox QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        msg.exec_()

    def start_animations(self):
        # 为功能列表添加淡入动画
        self.function_list.setStyleSheet(
            self.function_list.styleSheet() + "\nbackground-color: rgba(255, 255, 255, 0);")

        animation = QPropertyAnimation(self.function_list, b"pos")
        animation.setDuration(1000)
        animation.setStartValue(QPoint(self.function_list.x() - 50, self.function_list.y()))
        animation.setEndValue(QPoint(self.function_list.x(), self.function_list.y()))
        animation.setEasingCurve(QEasingCurve.OutBack)
        animation.start()

        # 为内容区域添加淡入动画
        self.content_stack.setStyleSheet(
            self.content_stack.styleSheet() + "\nbackground-color: rgba(255, 255, 255, 0);")

        fade_animation = QPropertyAnimation(self.content_stack, b"windowOpacity")
        fade_animation.setDuration(1000)
        fade_animation.setStartValue(0)
        fade_animation.setEndValue(1)
        fade_animation.setEasingCurve(QEasingCurve.OutCubic)
        fade_animation.start()

    def closeEvent(self, event):
        """窗口关闭事件"""
        try:
            # 停止正在运行的线程
            if hasattr(self, 'collection_thread') and self.collection_thread and self.collection_thread.isRunning():
                self.collection_thread.stop()
                self.collection_thread.wait()

            # 停止天气更新定时器
            if hasattr(self, 'weather_timer'):
                self.weather_timer.stop()

            # 保存当前设置
            self.save_settings()
        except Exception as e:
            logging.error(f"关闭窗口时发生错误: {str(e)}")
        super().closeEvent(event)

    def save_settings(self):
        """保存当前设置到配置文件"""
        try:
            settings = {}

            # 安全地获取主题设置
            theme_combo = self.findChild(QComboBox, 'theme_combo')
            if theme_combo:
                settings['theme'] = theme_combo.currentText()
            else:
                settings['theme'] = "深蓝主题"  # 默认主题

            # 安全地获取字体大小设置
            font_size_spin = self.findChild(QSpinBox, 'font_size_spin')
            if font_size_spin:
                settings['font_size'] = font_size_spin.value()
            else:
                settings['font_size'] = 14  # 默认字体大小

            # 安全地获取天气更新间隔设置
            weather_combo = self.findChild(QComboBox, 'weather_combo')
            if weather_combo:
                settings['weather_interval'] = weather_combo.currentText()
            else:
                settings['weather_interval'] = "30分钟"  # 默认更新间隔

            # 确保缓存目录存在
            if not os.path.exists(self.cache_dir):
                os.makedirs(self.cache_dir)

            settings_path = os.path.join(self.cache_dir, 'settings.json')
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)

            logging.info("设置已成功保存")
        except Exception as e:
            logging.error(f"保存设置失败: {str(e)}")
            import traceback
            traceback.print_exc()

    def load_settings(self):
        """加载保存的设置"""
        try:
            settings_path = os.path.join(self.cache_dir, 'settings.json')
            if not os.path.exists(self.cache_dir):
                logging.info("缓存目录不存在，将使用默认设置")
                return

            if not os.path.exists(settings_path):
                logging.info("设置文件不存在，将使用默认设置")
                return

            with open(settings_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)

                # 应用主题
                theme_combo = self.findChild(QComboBox, 'theme_combo')
                if theme_combo and 'theme' in settings:
                    theme_combo.setCurrentText(settings['theme'])

                # 应用字体大小
                font_size_spin = self.findChild(QSpinBox, 'font_size_spin')
                if font_size_spin and 'font_size' in settings:
                    font_size_spin.setValue(settings['font_size'])

                # 应用天气更新间隔
                weather_combo = self.findChild(QComboBox, 'weather_combo')
                if weather_combo and 'weather_interval' in settings:
                    weather_combo.setCurrentText(settings['weather_interval'])

            logging.info("设置已成功加载")
        except json.JSONDecodeError:
            logging.error("设置文件格式错误，将使用默认设置")
        except Exception as e:
            logging.error(f"加载设置失败: {str(e)}")
            import traceback
            traceback.print_exc()

    def create_data_analysis_page(self):
        """创建数据分析页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)

        # 创建标题
        title_label = QLabel("数据分析")
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

        # 创建分析结果展示区域
        self.analysis_tabs = QTabWidget()
        self.analysis_tabs.setStyleSheet("""
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

        # 创建趋势分析标签页
        trend_tab = QWidget()
        trend_layout = QVBoxLayout(trend_tab)
        trend_layout.setContentsMargins(0, 0, 0, 0)
        trend_layout.setSpacing(0)

        # 创建趋势图表显示区域
        self.trend_view = QWebEngineView()
        self.trend_view.setMinimumHeight(600)
        trend_layout.addWidget(self.trend_view)

        # 添加趋势分析标签页
        self.analysis_tabs.addTab(trend_tab, "趋势分析")

        # 创建空的人群画像标签页和需求图谱标签页
        self.portrait_tab = QWidget()
        self.demand_tab = QWidget()

        # 创建竞品分析标签页
        self.competitor_tab = QWidget()

        # 先添加空标签页到标签页控件
        self.analysis_tabs.addTab(trend_tab, "趋势分析")
        self.analysis_tabs.addTab(self.portrait_tab, "人群画像分析")
        self.analysis_tabs.addTab(self.demand_tab, "需求图谱分析")
        self.analysis_tabs.addTab(self.competitor_tab, "竞品分析")

        # 初始化标签页的内容
        self.init_portrait_tab()
        self.init_demand_tab()
        self.init_competitor_tab()  # 初始化竞品分析标签页

        layout.addWidget(self.analysis_tabs)
        return page

    def init_portrait_tab(self):
        """初始化人群画像标签页"""
        # 创建主布局
        layout = QVBoxLayout(self.portrait_tab)

        # 创建子标签页
        self.portrait_subtabs = QTabWidget()
        self.portrait_subtabs.setStyleSheet("""
            QTabWidget {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 5px;
            }
            QTabWidget::pane {
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 5px;
                padding: 5px;
            }
            QTabBar::tab {
                background: rgba(255, 255, 255, 0.1);
                color: white;
                padding: 6px 16px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: rgba(33, 150, 243, 0.5);
            }
        """)

        # 创建四个子标签页
        self.age_tab = QWidget()
        self.gender_tab = QWidget()
        self.region_tab = QWidget()
        self.interest_tab = QWidget()

        # 添加子标签页到标签控件
        self.portrait_subtabs.addTab(self.age_tab, "年龄分布")
        self.portrait_subtabs.addTab(self.gender_tab, "性别分布")
        self.portrait_subtabs.addTab(self.region_tab, "地域分布")
        self.portrait_subtabs.addTab(self.interest_tab, "兴趣分布")

        # 初始化各个子标签页内容
        self.init_age_tab()
        self.init_gender_tab()
        self.init_region_tab()
        self.init_interest_tab()

        # 将子标签控件添加到主布局
        layout.addWidget(self.portrait_subtabs)

        # 保存当前地域数据，以便在视图切换时使用
        self.current_region_data = None
        self.current_region_max_value = 0

    def init_age_tab(self):
        """初始化年龄分布标签页"""
        layout = QVBoxLayout(self.age_tab)

        # 创建年龄分布图表
        self.age_chart_view = QWebEngineView()
        self.age_chart_view.setMinimumHeight(500)

        layout.addWidget(self.age_chart_view)

    def init_gender_tab(self):
        """初始化性别分布标签页"""
        layout = QVBoxLayout(self.gender_tab)

        # 创建性别分布图表
        self.gender_chart_view = QWebEngineView()
        self.gender_chart_view.setMinimumHeight(500)

        layout.addWidget(self.gender_chart_view)

    def init_region_tab(self):
        """初始化地域分布标签页"""
        layout = QVBoxLayout(self.region_tab)

        # 添加视图选择下拉框
        view_layout = QHBoxLayout()
        view_label = QLabel("显示方式:")
        self.region_view_selector = QComboBox()
        self.region_view_selector.addItem("表格视图")
        self.region_view_selector.addItem("热力图")
        self.region_view_selector.currentIndexChanged.connect(self.on_region_view_changed)
        view_layout.addWidget(view_label)
        view_layout.addWidget(self.region_view_selector)
        view_layout.addStretch()

        # 创建地域分布图表
        self.region_map_view = QWebEngineView()
        self.region_map_view.setMinimumHeight(500)

        # 配置WebEngineView设置以允许本地文件访问
        settings = self.region_map_view.settings()
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.AllowRunningInsecureContent, True)

        layout.addLayout(view_layout)
        layout.addWidget(self.region_map_view)

    def init_interest_tab(self):
        """初始化兴趣分布标签页"""
        layout = QVBoxLayout(self.interest_tab)

        # 创建兴趣分布图表
        self.interest_chart_view = QWebEngineView()
        self.interest_chart_view.setMinimumHeight(500)

        layout.addWidget(self.interest_chart_view)

    def init_competitor_tab(self):
        """初始化竞品分析标签页"""
        layout = QVBoxLayout(self.competitor_tab)

        # 上部分：竞品关键词选择区域
        selection_frame = QFrame()
        selection_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        selection_layout = QVBoxLayout(selection_frame)

        # 说明文字
        help_label = QLabel("添加多个关键词进行对比分析，了解竞争态势")
        help_label.setStyleSheet("color: white; font-style: italic;")
        selection_layout.addWidget(help_label)

        # 关键词输入区域
        keywords_layout = QHBoxLayout()

        self.competitor_input = QLineEdit()
        self.competitor_input.setPlaceholderText("输入要比较的关键词")
        self.competitor_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 5px;
                color: white;
            }
        """)

        add_button = QPushButton("添加")
        add_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        add_button.clicked.connect(self.add_competitor_keyword)

        compare_button = QPushButton("开始比较")
        compare_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        compare_button.clicked.connect(self.compare_competitors)

        clear_button = QPushButton("清空")
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #F44336;
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
        """)
        clear_button.clicked.connect(self.clear_competitors)

        keywords_layout.addWidget(self.competitor_input)
        keywords_layout.addWidget(add_button)
        keywords_layout.addWidget(compare_button)
        keywords_layout.addWidget(clear_button)

        selection_layout.addLayout(keywords_layout)

        # 已添加的关键词列表
        list_label = QLabel("已添加的关键词:")
        list_label.setStyleSheet("color: white; margin-top: 10px;")
        selection_layout.addWidget(list_label)

        self.competitor_list = QListWidget()
        self.competitor_list.setStyleSheet("""
            QListWidget {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 5px;
                color: white;
                padding: 5px;
            }
            QListWidget::item {
                padding: 5px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            QListWidget::item:selected {
                background: rgba(33, 150, 243, 0.3);
            }
        """)
        self.competitor_list.setMaximumHeight(150)
        selection_layout.addWidget(self.competitor_list)

        # 将选择区域添加到主布局
        layout.addWidget(selection_frame)

        # 下部分：图表显示区域
        chart_frame = QFrame()
        chart_frame.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        chart_layout = QVBoxLayout(chart_frame)

        # 创建竞品分析图表
        self.competitor_chart_view = QWebEngineView()
        self.competitor_chart_view.setMinimumHeight(450)
        chart_layout.addWidget(self.competitor_chart_view)

        # 分析结果文本区域
        result_label = QLabel("分析结果:")
        result_label.setStyleSheet("color: white; margin-top: 10px;")
        chart_layout.addWidget(result_label)

        self.competitor_result = QTextEdit()
        self.competitor_result.setReadOnly(True)
        self.competitor_result.setStyleSheet("""
            QTextEdit {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 5px;
                color: white;
                padding: 10px;
            }
        """)
        self.competitor_result.setMaximumHeight(150)
        chart_layout.addWidget(self.competitor_result)

        # 将图表区域添加到主布局
        layout.addWidget(chart_frame)

        # 初始化数据
        self.competitor_keywords = []

    def add_competitor_keyword(self):
        """添加竞品关键词到列表"""
        keyword = self.competitor_input.text().strip()
        if not keyword:
            self.show_message("提示", "请输入关键词")
            return

        if keyword in self.competitor_keywords:
            self.show_message("提示", f"关键词 '{keyword}' 已在列表中")
            return

        # 限制最多5个关键词
        if len(self.competitor_keywords) >= 5:
            self.show_message("提示", "最多只能添加5个关键词进行比较")
            return

        self.competitor_keywords.append(keyword)
        self.competitor_list.addItem(keyword)
        self.competitor_input.clear()

    def clear_competitors(self):
        """清空竞品关键词列表"""
        self.competitor_keywords = []
        self.competitor_list.clear()
        self.competitor_chart_view.setHtml("")
        self.competitor_result.clear()

    def compare_competitors(self):
        """比较多个关键词的趋势数据"""
        if not self.competitor_keywords:
            self.show_message("提示", "请先添加要比较的关键词")
            return

        try:
            # 连接数据库
            connection = db_utils.get_connection()
            cursor = connection.cursor()

            all_keyword_data = {}
            earliest_date = None
            latest_date = None

            # 查询每个关键词的趋势数据
            for keyword in self.competitor_keywords:
                query = """
                SELECT date, index_value
                FROM baidu_index_trends 
                WHERE keyword = %s 
                ORDER BY date
                """
                cursor.execute(query, (keyword,))
                results = cursor.fetchall()

                if not results:
                    self.show_message("提示", f"未找到关键词 '{keyword}' 的趋势数据")
                    continue

                # 提取数据
                dates = []
                values = []

                for row in results:
                    if row[0] and hasattr(row[0], 'strftime'):
                        date_str = row[0].strftime('%Y-%m-%d')
                    else:
                        date_str = str(row[0])

                    dates.append(date_str)
                    values.append(float(row[1]) if row[1] is not None else 0)

                # 更新日期范围
                if earliest_date is None or dates[0] < earliest_date:
                    earliest_date = dates[0]
                if latest_date is None or dates[-1] > latest_date:
                    latest_date = dates[-1]

                all_keyword_data[keyword] = {
                    'dates': dates,
                    'values': values
                }

            cursor.close()
            connection.close()

            if not all_keyword_data:
                self.show_message("提示", "没有找到任何关键词的数据")
                return

            # 生成竞品分析图表
            self.generate_competitor_chart(all_keyword_data)

            # 生成分析结果
            self.generate_competitor_analysis(all_keyword_data, earliest_date, latest_date)

        except Exception as e:
            logging.error(f"竞品分析失败: {str(e)}")
            self.show_message("错误", f"竞品分析失败: {str(e)}")

    def generate_competitor_chart(self, all_keyword_data):
        """生成竞品比较图表"""
        # 使用pyecharts创建折线图
        line = Line(init_opts=opts.InitOpts(
            width="100%",
            height="450px",
            bg_color="#1a237e",
            renderer="canvas"
        ))

        # 合并所有日期并去重
        all_dates = set()
        for keyword_data in all_keyword_data.values():
            all_dates.update(keyword_data['dates'])

        all_dates = sorted(list(all_dates))

        # 添加X轴数据
        line.add_xaxis(all_dates)

        # 为每个关键词添加一条线
        colors = ["#4CAF50", "#FF5722", "#2196F3", "#9C27B0", "#FFC107"]  # 为5个关键词预设颜色

        for i, (keyword, data) in enumerate(all_keyword_data.items()):
            # 需要将数据映射到统一的日期轴上
            values_dict = dict(zip(data['dates'], data['values']))
            aligned_values = [values_dict.get(date, None) for date in all_dates]

            # 对缺失值进行插值处理
            for j in range(len(aligned_values)):
                if aligned_values[j] is None:
                    # 向前找最近的非None值
                    prev_value = None
                    for k in range(j - 1, -1, -1):
                        if aligned_values[k] is not None:
                            prev_value = aligned_values[k]
                            break

                    # 向后找最近的非None值
                    next_value = None
                    for k in range(j + 1, len(aligned_values)):
                        if aligned_values[k] is not None:
                            next_value = aligned_values[k]
                            break

                    # 线性插值
                    if prev_value is not None and next_value is not None:
                        aligned_values[j] = (prev_value + next_value) / 2
                    elif prev_value is not None:
                        aligned_values[j] = prev_value
                    elif next_value is not None:
                        aligned_values[j] = next_value
                    else:
                        aligned_values[j] = 0

            color = colors[i % len(colors)]

            line.add_yaxis(
                keyword,
                aligned_values,
                is_smooth=True,
                symbol_size=6,
                linestyle_opts=opts.LineStyleOpts(width=2, color=color),
                itemstyle_opts=opts.ItemStyleOpts(color=color),
                label_opts=opts.LabelOpts(is_show=False)
            )

        # 设置全局选项
        line.set_global_opts(
            title_opts=opts.TitleOpts(
                title="关键词竞争趋势对比",
                subtitle="数据来源：百度指数",
                pos_left="center",
                title_textstyle_opts=opts.TextStyleOpts(color="#FFFFFF", font_size=18),
                subtitle_textstyle_opts=opts.TextStyleOpts(color="#B0BEC5", font_size=12)
            ),
            tooltip_opts=opts.TooltipOpts(
                trigger="axis",
                axis_pointer_type="cross",
                background_color="rgba(50,50,50,0.7)",
                border_color="#ccc",
                textstyle_opts=opts.TextStyleOpts(color="#fff")
            ),
            legend_opts=opts.LegendOpts(
                pos_top="8%",
                pos_left="center",
                orient="horizontal",
                textstyle_opts=opts.TextStyleOpts(color="#fff")
            ),
            toolbox_opts=opts.ToolboxOpts(
                is_show=True,
                feature={
                    "dataZoom": {"yAxisIndex": "none"},
                    "restore": {},
                    "saveAsImage": {}
                }
            ),
            xaxis_opts=opts.AxisOpts(
                type_="category",
                boundary_gap=False,
                axislabel_opts=opts.LabelOpts(rotate=45, color="#B0BEC5", interval="auto", margin=8),
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color="#B0BEC5"))
            ),
            yaxis_opts=opts.AxisOpts(
                type_="value",
                name="搜索指数",
                name_textstyle_opts=opts.TextStyleOpts(color="#B0BEC5"),
                axislabel_opts=opts.LabelOpts(color="#B0BEC5"),
                axisline_opts=opts.AxisLineOpts(linestyle_opts=opts.LineStyleOpts(color="#B0BEC5"))
            ),
            datazoom_opts=[
                opts.DataZoomOpts(
                    range_start=70,
                    range_end=100,
                    pos_bottom="5%"
                ),
                opts.DataZoomOpts(type_="inside")
            ]
        )

        # 渲染图表
        html = line.render_embed()

        # 添加自定义CSS
        custom_css = """
        <style>
            html, body {
                margin: 0;
                padding: 0;
                width: 100%;
                height: 100%;
                background-color: #1a237e;
            }
            .chart-container {
                width: 100%;
                height: 100%;
            }
        </style>
        """

        final_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            {custom_css}
        </head>
        <body>
            <div class="chart-container">
                {html}
            </div>
        </body>
        </html>
        """

        self.competitor_chart_view.setHtml(final_html)

    def generate_competitor_analysis(self, all_keyword_data, earliest_date, latest_date):
        """生成竞品分析结果"""
        analysis_text = f"<h3>竞品分析结果</h3>"
        analysis_text += f"<p>分析期间: {earliest_date} 至 {latest_date}</p>"

        # 计算各关键词的平均值、最大值、增长率
        keyword_stats = {}

        for keyword, data in all_keyword_data.items():
            values = data['values']
            if not values:
                continue

            avg_value = sum(values) / len(values)
            max_value = max(values)
            min_value = min(values)

            # 计算增长率 (最后值 - 首值) / 首值 * 100%
            if values[0] > 0:
                growth_rate = (values[-1] - values[0]) / values[0] * 100
            else:
                growth_rate = 0

            # 计算波动率 (标准差 / 平均值)
            if avg_value > 0:
                std_dev = (sum((x - avg_value) ** 2 for x in values) / len(values)) ** 0.5
                volatility = std_dev / avg_value * 100
            else:
                volatility = 0

            keyword_stats[keyword] = {
                'avg': avg_value,
                'max': max_value,
                'min': min_value,
                'growth_rate': growth_rate,
                'volatility': volatility
            }

        # 对关键词进行排名（按平均值降序）
        ranked_keywords = sorted(keyword_stats.keys(), key=lambda k: keyword_stats[k]['avg'], reverse=True)

        # 生成排名表格
        analysis_text += "<h4>关键词排名（按平均搜索指数）</h4>"
        analysis_text += "<table style='width:100%; border-collapse:collapse;'>"
        analysis_text += "<tr style='background-color:rgba(255,255,255,0.2);'><th>排名</th><th>关键词</th><th>平均指数</th><th>最高指数</th><th>增长率</th></tr>"

        for i, keyword in enumerate(ranked_keywords):
            stats = keyword_stats[keyword]
            growth_color = "#4CAF50" if stats['growth_rate'] >= 0 else "#F44336"
            analysis_text += f"<tr><td>{i + 1}</td><td>{keyword}</td><td>{stats['avg']:.1f}</td><td>{stats['max']}</td>"
            analysis_text += f"<td style='color:{growth_color}'>{stats['growth_rate']:.1f}%</td></tr>"

        analysis_text += "</table>"

        # 为排名第一的关键词提供分析
        if ranked_keywords:
            top_keyword = ranked_keywords[0]
            analysis_text += f"<h4>领先关键词分析</h4>"
            analysis_text += f"<p>'{top_keyword}' 在竞争中处于领先地位，平均搜索指数为 {keyword_stats[top_keyword]['avg']:.1f}，"

            if keyword_stats[top_keyword]['growth_rate'] > 0:
                analysis_text += f"搜索趋势呈上升态势，增长率为 {keyword_stats[top_keyword]['growth_rate']:.1f}%。"
            else:
                analysis_text += f"搜索趋势呈下降态势，降低率为 {abs(keyword_stats[top_keyword]['growth_rate']):.1f}%。"

            if keyword_stats[top_keyword]['volatility'] > 30:
                analysis_text += f" 波动率较高 ({keyword_stats[top_keyword]['volatility']:.1f}%)，表明市场需求不稳定。"
            else:
                analysis_text += f" 波动率适中 ({keyword_stats[top_keyword]['volatility']:.1f}%)，表明市场需求相对稳定。"

            analysis_text += "</p>"

        # 设置结果
        self.competitor_result.setHtml(analysis_text)

    def on_region_view_changed(self, index):
        """处理地域分布视图切换"""
        print(f"切换地域分布视图: {index}")
        if not hasattr(self, 'current_region_data') or not self.current_region_data:
            print("没有地域数据可供显示")
            return

        if index == 0:  # 表格视图
            self.update_region_table_view(self.current_region_data, self.current_region_max_value)
        else:  # 热力图视图
            self.update_region_heatmap_view(self.current_region_data, self.current_region_max_value)

    def update_region_heatmap_view(self, region_data, max_value):
        """显示地域分布热力图视图"""
        try:
            import json
            import math
            import os
            print("渲染热力图视图...")

            # 确定资源文件路径
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            resources_dir = os.path.join(base_dir, "resources")

            # 获取文件路径
            echarts_js_path = os.path.join(resources_dir, "echarts.min.js")
            china_js_path = os.path.join(resources_dir, "china.js")

            # 检查文件存在
            echarts_exists = os.path.exists(echarts_js_path)
            china_exists = os.path.exists(china_js_path)

            # 监听URL变化事件，如果包含fallback参数，切换到表格视图
            self.region_map_view.urlChanged.connect(self.handle_url_changed)

            # 创建嵌入HTML的WebView
            if not echarts_exists:
                print("本地未找到ECharts库文件，将使用表格视图")
                self.region_view_selector.setCurrentIndex(0)  # 切换到表格视图
                return

            # 直接读取JS文件内容
            echarts_js = ''
            china_js = ''

            try:
                with open(echarts_js_path, 'r', encoding='utf-8') as f:
                    echarts_js = f.read()
                    print(f"已读取echarts.min.js，大小: {len(echarts_js)} 字节")
            except Exception as e:
                print(f"读取echarts.min.js失败: {str(e)}")
                self.region_view_selector.setCurrentIndex(0)  # 切换到表格视图
                return

            if china_exists:
                try:
                    with open(china_js_path, 'r', encoding='utf-8') as f:
                        china_js = f.read()
                        print(f"已读取china.js，大小: {len(china_js)} 字节")
                except Exception as e:
                    print(f"读取china.js失败: {str(e)}")
                    china_js = ''

            # 转换为JSON字符串，用于ECharts
            # 确保处理数据中的NaN值
            processed_data = []
            for item in region_data:
                value = item['value']
                if isinstance(value, (int, float)) and not math.isnan(value):
                    processed_data.append({"name": item['name'], "value": value})
                else:
                    processed_data.append({"name": item['name'], "value": 0})

            map_data_json = json.dumps(processed_data)

            # 创建直接内嵌ECharts代码和地图数据的HTML
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>地域分布热力图</title>
                <style>
                    body, html {{
                        margin: 0;
                        padding: 0;
                        background-color: #1a237e;
                        color: white;
                        font-family: Arial, sans-serif;
                        width: 100%;
                        height: 100%;
                        overflow: hidden;
                    }}
                    #main {{
                        width: 100%;
                        height: 600px;
                    }}
                    #error-log {{
                        position: absolute;
                        bottom: 0;
                        left: 0;
                        right: 0;
                        color: #ff5722;
                        background-color: rgba(0,0,0,0.5);
                        padding: 5px;
                        font-size: 12px;
                        height: 100px;
                        overflow: auto;
                        display: block;
                    }}
                    .error {{
                        color: #ff5722;
                    }}
                    .success {{
                        color: #4caf50;
                    }}
                    .fallback {{
                        text-align: center;
                        padding-top: 100px;
                    }}
                </style>
                <script>
                    {echarts_js}
                </script>
                <script>
                    {china_js}
                </script>
            </head>
            <body>
                <div id="main"></div>
                <div id="error-log"></div>

                <script>
                // 调试函数
                function log(message, isError) {{
                    var logElement = document.getElementById('error-log');
                    var p = document.createElement('p');
                    p.className = isError ? 'error' : 'success';
                    p.textContent = message;
                    logElement.appendChild(p);
                    console.log(message);
                }}

                // 页面加载完成
                window.onload = function() {{
                    try {{
                        log("页面加载完成，开始初始化...");

                        if (typeof echarts === 'undefined') {{
                            log("ECharts未加载，切换到表格视图", true);
                            showFallback();
                            return;
                        }}

                        log("ECharts已成功加载，开始渲染地图...");
                        renderChart();
                    }} catch (e) {{
                        log("初始化出错: " + e.message, true);
                        showFallback();
                    }}
                }};

                function renderChart() {{
                    try {{
                        log("开始渲染热力图...");
                        // 初始化ECharts实例
                        var chart = echarts.init(document.getElementById('main'));

                        // 准备数据
                        var mapData = {map_data_json};
                        var maxValue = {max_value};

                        // 检查数据
                        log("地图数据准备完成: " + mapData.length + " 条数据");

                        // 配置选项
                        var option = {{
                            title: {{
                                text: '地域分布热力图',
                                subtext: '基于百度指数的地域分布数据',
                                left: 'center',
                                textStyle: {{
                                    color: '#ffffff'
                                }},
                                subtextStyle: {{
                                    color: '#cccccc'
                                }}
                            }},
                            tooltip: {{
                                trigger: 'item',
                                formatter: function(params) {{
                                    // 保证值始终是有效数字
                                    var value = params.value;
                                    if (value === undefined || isNaN(value)) {{
                                        value = 0;
                                    }}
                                    return params.name + '<br/>搜索指数: ' + value;
                                }}
                            }},
                            toolbox: {{
                                show: true,
                                orient: 'vertical',
                                left: 'right',
                                top: 'center',
                                feature: {{
                                    dataView: {{readOnly: false}},
                                    restore: {{}},
                                    saveAsImage: {{}}
                                }},
                                iconStyle: {{
                                    color: '#ffffff'
                                }}
                            }},
                            visualMap: {{
                                min: 0,
                                max: maxValue,
                                left: '10%',
                                top: 'middle',
                                text: ['高', '低'],
                                calculable: true,
                                inRange: {{
                                    color: ['#C6E2FF', '#1E90FF', '#002366']
                                }},
                                textStyle: {{
                                    color: '#fff'
                                }}
                            }},
                            series: [
                                {{
                                    name: '搜索指数',
                                    type: 'map',
                                    map: 'china',
                                    roam: true,
                                    zoom: 1.2,
                                    scaleLimit: {{
                                        min: 0.5,
                                        max: 3
                                    }},
                                    itemStyle: {{
                                        areaColor: '#323c48',
                                        borderColor: '#111'
                                    }},
                                    emphasis: {{
                                        itemStyle: {{
                                            areaColor: '#ff5722'
                                        }},
                                        label: {{
                                            show: true,
                                            color: '#fff'
                                        }}
                                    }},
                                    data: mapData
                                }}
                            ]
                        }};

                        // 应用配置
                        chart.setOption(option);
                        log("热力图渲染完成");

                        // 窗口大小改变时重新调整大小
                        window.addEventListener('resize', function() {{
                            chart.resize();
                        }});

                        // 10秒后隐藏日志
                        setTimeout(function() {{
                            var logElement = document.getElementById('error-log');
                            logElement.style.height = '20px';
                            logElement.style.opacity = '0.5';
                        }}, 10000);
                    }} catch (e) {{
                        log("渲染图表失败: " + e.message, true);
                        showFallback();
                    }}
                }}

                function showFallback() {{
                    log("显示备用表格视图", false);
                    document.getElementById('main').innerHTML = `
                    <div class="fallback">
                        <h2>热力图加载失败</h2>
                        <p>正在为您显示备用表格数据...</p>
                    </div>
                    `;

                    // 通知PyQt跳转到表格视图
                    setTimeout(function() {{
                        window.location.href = 'about:blank?fallback=true';
                    }}, 2000);
                }}
                </script>
            </body>
            </html>
            """

            # 更新地图显示
            self.region_map_view.setHtml(html)
            print("热力图HTML已更新")

        except Exception as e:
            import logging
            logging.error(f"更新地域分布热力图时出错: {str(e)}")
            print(f"错误: {str(e)}")
            import traceback
            traceback.print_exc()

            # 如果出现错误，尝试切换到表格视图
            try:
                if hasattr(self, 'region_view_selector'):
                    self.region_view_selector.setCurrentIndex(0)  # 切换到表格视图
            except:
                pass

    def handle_navigation_request(self, url):
        """处理导航请求"""
        url_str = url.toString()
        print(f"导航到: {url_str}")
        if 'fallback=true' in url_str:
            print("检测到热力图失败，切换到表格视图")
            # 切换到表格视图
            self.region_view_selector.setCurrentIndex(0)

    def handle_url_changed(self, url):
        """处理URL改变事件"""
        url_str = url.toString()
        print(f"URL改变: {url_str}")
        if 'fallback=true' in url_str:
            print("检测到热力图失败，切换到表格视图")
            # 切换到表格视图
            self.region_view_selector.setCurrentIndex(0)

    def init_demand_tab(self):
        """初始化需求图谱标签页"""
        layout = QVBoxLayout(self.demand_tab)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 标题
        title_label = QLabel("需求图谱分析")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white;")
        layout.addWidget(title_label)

        # 创建表格
        self.demand_table = QTableWidget()
        self.demand_table.setStyleSheet("""
            QTableWidget {
                background-color: rgba(255, 255, 255, 0.1);
                color: white;
                border: 1px solid rgba(255, 255, 255, 0.2);
                border-radius: 5px;
                gridline-color: rgba(255, 255, 255, 0.1);
            }
            QHeaderView::section {
                background-color: rgba(33, 150, 243, 0.8);
                color: white;
                padding: 8px;
                border: 1px solid rgba(255, 255, 255, 0.1);
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
                background-color: rgba(255, 255, 255, 0.05);
            }
            QTableWidget::item:selected {
                background-color: rgba(33, 150, 243, 0.5);
                color: white;
            }
        """)

        # 设置表格属性
        self.demand_table.setAlternatingRowColors(False)  # 关闭交替行颜色
        self.demand_table.horizontalHeader().setStretchLastSection(True)
        self.demand_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.demand_table.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.demand_table.verticalHeader().setDefaultSectionSize(40)

        # 设置选择行为
        self.demand_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.demand_table.setSelectionMode(QTableWidget.SingleSelection)

        layout.addWidget(self.demand_table)

        # 添加Web视图用于显示图表
        self.demand_view = QWebEngineView()
        self.demand_view.setMinimumHeight(400)
        layout.addWidget(self.demand_view)

        # 默认显示无数据提示
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {
                    background-color: #1a237e;
                    color: white;
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                .message {
                    text-align: center;
                    padding: 20px;
                }
                h2 {
                    margin-bottom: 10px;
                }
            </style>
        </head>
        <body>
            <div class="message">
                <h2>暂无需求图谱数据</h2>
                <p>请先进行数据采集</p>
            </div>
        </body>
        </html>
        """
        self.demand_view.setHtml(html)

    def analyze_data(self, keyword=None):
        """执行数据分析"""
        try:
            print("开始数据分析...")

            # 连接数据库
            print("正在连接数据库...")
            connection = db_utils.get_connection()
            cursor = connection.cursor()
            print("数据库连接成功")

            # 如果没有传入关键词，尝试从采集页面获取
            if keyword is None:
                keyword = self.keyword_input.text()
                print(f"使用输入框关键词: {keyword}")

            if not keyword:
                print("未找到关键词")
                QMessageBox.warning(self, "错误", "未找到关键词")
                return

            print(f"开始分析关键词: {keyword}")

            # 获取最新的日期
            print("正在查询最新日期...")
            date_query = """
            SELECT DISTINCT date 
            FROM crowd_region_data 
            WHERE keyword = %s
            ORDER BY date DESC 
            LIMIT 1
            """
            cursor.execute(date_query, (keyword,))
            latest_date = cursor.fetchone()
            print(f"查询到的最新日期: {latest_date}")

            if not latest_date:
                print("未找到相关数据，尝试其他表...")
                # 尝试从其他表获取日期
                date_query = """
                SELECT DISTINCT data_date 
                FROM crowd_interest_data 
                WHERE keyword = %s
                ORDER BY data_date DESC 
                LIMIT 1
                """
                cursor.execute(date_query, (keyword,))
                latest_date = cursor.fetchone()
                print(f"从crowd_interest_data查询到的日期: {latest_date}")

            if not latest_date:
                print("所有表中都未找到数据")
                QMessageBox.warning(self, "错误", "未找到相关数据")
                cursor.close()
                connection.close()
                return

            selected_date = latest_date[0]
            # 检查日期类型并转换
            if selected_date and hasattr(selected_date, 'strftime'):
                selected_date = selected_date.strftime('%Y-%m-%d')
            elif selected_date and isinstance(selected_date, str):
                # 已经是字符串格式，不需要转换
                pass
            else:
                # 转换为字符串以避免类型问题
                selected_date = str(selected_date)

            print(f"使用日期: {selected_date}")

            try:
                print("开始分析趋势数据...")
                self.analyze_trend_data(cursor, keyword, selected_date)
                print("趋势数据分析完成")
            except Exception as e:
                print(f"趋势数据分析失败: {str(e)}")
                logging.error(f"趋势数据分析失败: {str(e)}")

            try:
                print("开始分析人群画像数据...")
                self.analyze_portrait_data(cursor, keyword, selected_date)
                print("人群画像数据分析完成")
            except Exception as e:
                print(f"人群画像数据分析失败: {str(e)}")
                logging.error(f"人群画像数据分析失败: {str(e)}")

            try:
                print("开始分析需求图谱数据...")
                self.analyze_demand_data(cursor, keyword, selected_date)
                print("需求图谱数据分析完成")
            except Exception as e:
                print(f"需求图谱数据分析失败: {str(e)}")
                logging.error(f"需求图谱数据分析失败: {str(e)}")

            print("所有数据分析完成")
            cursor.close()
            connection.close()

        except Exception as e:
            print(f"数据分析过程中发生错误: {str(e)}")
            logging.error(f"数据分析失败: {str(e)}")
            QMessageBox.warning(self, "错误", f"数据分析失败: {str(e)}")
            if 'cursor' in locals():
                cursor.close()
            if 'connection' in locals():
                connection.close()

    def analyze_trend_data(self, cursor, keyword, date):
        """分析趋势数据"""
        try:
            # 查询趋势数据
            query = """
            SELECT date, index_value, area 
            FROM baidu_index_trends 
            WHERE keyword = %s 
            ORDER BY date
            """
            cursor.execute(query, (keyword,))
            results = cursor.fetchall()

            if not results:
                return

            # 处理数据 - 显示更多数据点并优化最近数据
            total_points = len(results)

            # 增加数据点数量，从100增加到300
            sample_size = min(total_points, 300)

            # 如果总数据点小于或等于300，直接全部显示
            if total_points <= sample_size:
                dates = []
                values = []
                for row in results:
                    if row[0] and hasattr(row[0], 'strftime'):
                        dates.append(row[0].strftime('%Y-%m-%d'))
                    else:
                        dates.append(str(row[0]))
                    values.append(float(row[1]) if row[1] is not None else 0)
            else:
                # 优先显示最近的数据，并在早期数据中采样
                # 计算前1/3的数据进行采样，后2/3的数据全部显示
                early_data_count = total_points // 3
                recent_data_count = total_points - early_data_count

                # 采样早期数据
                early_sample_size = min(early_data_count, sample_size - recent_data_count)
                early_step = max(1, early_data_count // early_sample_size)

                dates = []
                values = []

                # 对早期数据进行采样
                for i in range(0, early_data_count, early_step):
                    row = results[i]
                    if row[0] and hasattr(row[0], 'strftime'):
                        dates.append(row[0].strftime('%Y-%m-%d'))
                    else:
                        dates.append(str(row[0]))
                    values.append(float(row[1]) if row[1] is not None else 0)

                # 显示全部最近数据
                for i in range(early_data_count, total_points):
                    row = results[i]
                    if row[0] and hasattr(row[0], 'strftime'):
                        dates.append(row[0].strftime('%Y-%m-%d'))
                    else:
                        dates.append(str(row[0]))
                    values.append(float(row[1]) if row[1] is not None else 0)

            # 使用pyecharts创建趋势图
            line = Line(init_opts=opts.InitOpts(
                width="100%",
                height="800px",
                bg_color="#1a237e",
                renderer="canvas",  # 使用canvas渲染器提高性能
                animation_opts=opts.AnimationOpts(animation=False)  # 关闭动画提高性能
            ))

            # 添加数据
            line.add_xaxis(dates)
            line.add_yaxis(
                keyword,
                values,
                is_smooth=False,  # 关闭平滑曲线提高性能
                symbol="none",  # 不显示数据点提高性能
                label_opts=opts.LabelOpts(is_show=False),  # 不显示标签提高性能
                linestyle_opts=opts.LineStyleOpts(
                    width=2,
                    type_="solid",
                    color="#4FC3F7"
                )
            )

            # 优化全局配置，默认显示最近30%的数据
            line.set_global_opts(
                title_opts=opts.TitleOpts(
                    title=f"{keyword}搜索趋势",
                    subtitle="数据来源：百度指数",
                    pos_left="center",
                    title_textstyle_opts=opts.TextStyleOpts(
                        color="#FFFFFF",
                        font_size=20
                    ),
                    subtitle_textstyle_opts=opts.TextStyleOpts(
                        color="#B0BEC5",
                        font_size=12
                    )
                ),
                tooltip_opts=opts.TooltipOpts(
                    trigger="axis",
                    axis_pointer_type="line",  # 使用直线指示器提高性能
                    background_color="rgba(50,50,50,0.7)",
                    border_color="#ccc",
                    textstyle_opts=opts.TextStyleOpts(color="#fff")
                ),
                toolbox_opts=opts.ToolboxOpts(
                    is_show=True,
                    pos_left="right",
                    feature={
                        "dataZoom": {"yAxisIndex": "none"},
                        "restore": {},
                        "saveAsImage": {}
                    }
                ),
                xaxis_opts=opts.AxisOpts(
                    type_="category",
                    boundary_gap=False,
                    axislabel_opts=opts.LabelOpts(
                        rotate=45,
                        color="#B0BEC5",
                        interval="auto",  # 自动计算标签间隔
                        margin=8
                    ),
                    axisline_opts=opts.AxisLineOpts(
                        linestyle_opts=opts.LineStyleOpts(color="#B0BEC5")
                    ),
                    splitline_opts=opts.SplitLineOpts(is_show=False)  # 不显示分割线提高性能
                ),
                yaxis_opts=opts.AxisOpts(
                    type_="value",
                    name="搜索指数",
                    name_textstyle_opts=opts.TextStyleOpts(color="#B0BEC5"),
                    axislabel_opts=opts.LabelOpts(color="#B0BEC5"),
                    axisline_opts=opts.AxisLineOpts(
                        linestyle_opts=opts.LineStyleOpts(color="#B0BEC5")
                    ),
                    splitline_opts=opts.SplitLineOpts(is_show=False)  # 不显示分割线提高性能
                ),
                datazoom_opts=[
                    opts.DataZoomOpts(
                        is_show=True,
                        type_="slider",
                        # 默认只显示最近30%的数据
                        range_start=70,
                        range_end=100,
                        pos_bottom="5%"
                    ),
                    # 添加内部框选区域缩放组件
                    opts.DataZoomOpts(
                        type_="inside"
                    )
                ],
                legend_opts=opts.LegendOpts(
                    is_show=False  # 不显示图例提高性能
                )
            )

            # 优化HTML模板
            custom_css = """
            <style>
                html, body {
                    margin: 0;
                    padding: 0;
                    width: 100%;
                    height: 100%;
                    background-color: #1a237e;
                }
                .chart-container {
                    width: 100%;
                    height: 100%;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }
                #chart {
                    width: 100% !important;
                    height: 800px !important;
                }
            </style>
            """

            # 简化HTML内容
            final_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                {custom_css}
            </head>
            <body>
                <div class="chart-container">
                    <div id="chart">
                        {line.render_embed()}
                    </div>
                </div>
            </body>
            </html>
            """

            # 将图表渲染到HTML并显示
            self.trend_view.setHtml(final_html)

        except Exception as e:
            logging.error(f"分析趋势数据失败: {str(e)}")
            raise

    def analyze_portrait_data(self, cursor, keyword, date):
        """分析人群画像数据"""
        try:
            # 将字符串日期转换为datetime.date对象，并处理可能的类型问题
            if date and isinstance(date, str):
                try:
                    # 使用导入的datetime，而不是datetime.datetime
                    from datetime import datetime as dt
                    date = dt.strptime(date, '%Y-%m-%d').date()
                except ValueError:
                    # 如果日期格式不正确，记录错误但继续使用原始值
                    logging.error(f"无法解析日期字符串: {date}")
                    # 不修改date值，使用原始值继续

            print(f"Debug - 查询参数: keyword={keyword}, date={date}, date类型={type(date)}")

            # 激活人群画像标签页
            self.analysis_tabs.setCurrentWidget(self.portrait_tab)

            # 先检查地域数据表中的可用日期
            check_region_query = "SELECT DISTINCT date FROM crowd_region_data WHERE keyword = %s ORDER BY date DESC"
            cursor.execute(check_region_query, (keyword,))
            region_dates = cursor.fetchall()
            print(f"Debug - 地域数据可用日期: {region_dates}")

            # 检查年龄数据表中的可用日期
            check_age_query = "SELECT DISTINCT date FROM crowd_age_data WHERE keyword = %s ORDER BY date DESC"
            cursor.execute(check_age_query, (keyword,))
            age_dates = cursor.fetchall()
            print(f"Debug - 年龄数据可用日期: {age_dates}")

            # 检查性别数据表中的可用日期
            check_gender_query = "SELECT DISTINCT date FROM crowd_gender_data WHERE keyword = %s ORDER BY date DESC"
            cursor.execute(check_gender_query, (keyword,))
            gender_dates = cursor.fetchall()
            print(f"Debug - 性别数据可用日期: {gender_dates}")

            # 检查兴趣数据表中的可用日期
            check_interest_query = "SELECT DISTINCT data_date FROM crowd_interest_data WHERE keyword = %s ORDER BY data_date DESC"
            cursor.execute(check_interest_query, (keyword,))
            interest_dates = cursor.fetchall()
            print(f"Debug - 兴趣数据可用日期: {interest_dates}")

            # 处理地域分布数据
            if region_dates:
                # 使用最新的可用日期
                region_latest_date = region_dates[0][0]
                print(f"Debug - 使用地域数据最新可用日期: {region_latest_date}")

                # 查询地域分布数据 - 修改SQL确保数据类型正确
                region_query = """
                SELECT province, value
                FROM crowd_region_data
                WHERE keyword = %s AND date = %s
                AND value IS NOT NULL AND value != 'NULL' AND value > 0
                ORDER BY value DESC
                """
                cursor.execute(region_query, (keyword, region_latest_date))
                region_results = cursor.fetchall()
                print(f"Debug - 地域分布查询结果: {region_results}")

                if region_results:
                    # 验证数据是否有效
                    has_valid_data = False
                    for province, value in region_results:
                        try:
                            # 检查值是否可以转换为浮点数
                            float_val = float(value) if value is not None else 0
                            if float_val > 0:
                                has_valid_data = True
                                break
                        except (ValueError, TypeError):
                            continue

                    if has_valid_data:
                        # 直接更新地域分布图表并切换到地域分布标签页
                        self.update_region_chart(region_results)
                        self.portrait_subtabs.setCurrentWidget(self.region_tab)
                    else:
                        print(f"No region distribution data found for keyword {keyword}")
                else:
                    print(f"No available dates found for keyword {keyword} in region data")
            else:
                print(f"No available dates found for keyword {keyword} in region data")

            # 处理年龄分布数据
            if age_dates:
                age_latest_date = age_dates[0][0]
                print(f"Debug - 使用年龄数据最新可用日期: {age_latest_date}")

                age_query = """
                SELECT name, rate, tgi
                FROM crowd_age_data
                WHERE keyword = %s AND date = %s
                ORDER BY CAST(rate AS DECIMAL) DESC
                """
                cursor.execute(age_query, (keyword, age_latest_date))
                age_results = cursor.fetchall()
                if age_results:
                    print(f"获取到年龄分布数据: {len(age_results)}条")
                    self.update_age_chart(age_results)
                else:
                    print(f"No age distribution data found for keyword {keyword} and date {age_latest_date}")
            else:
                print(f"No age distribution data found for keyword {keyword}")

            # 处理性别分布数据
            if gender_dates:
                gender_latest_date = gender_dates[0][0]
                print(f"Debug - 使用性别数据最新可用日期: {gender_latest_date}")

                gender_query = """
                SELECT name, rate, tgi
                FROM crowd_gender_data
                WHERE keyword = %s AND date = %s
                ORDER BY CAST(rate AS DECIMAL) DESC
                """
                cursor.execute(gender_query, (keyword, gender_latest_date))
                gender_results = cursor.fetchall()
                if gender_results:
                    print(f"获取到性别分布数据: {len(gender_results)}条")
                    self.update_gender_chart(gender_results)
                else:
                    print(f"No gender distribution data found for keyword {keyword} and date {gender_latest_date}")
            else:
                print(f"No gender distribution data found for keyword {keyword}")

            # 处理兴趣分布数据
            if interest_dates:
                interest_latest_date = interest_dates[0][0]
                print(f"Debug - 使用兴趣数据最新可用日期: {interest_latest_date}")

                interest_query = """
                SELECT category, name, value, tgi, rate
                FROM crowd_interest_data
                WHERE keyword = %s AND data_date = %s
                ORDER BY CAST(value AS DECIMAL) DESC
                """
                cursor.execute(interest_query, (keyword, interest_latest_date))
                interest_results = cursor.fetchall()
                if interest_results:
                    print(f"获取到兴趣分布数据: {len(interest_results)}条")
                    self.update_interest_chart(interest_results)
                else:
                    print(f"No interest distribution data found for keyword {keyword} and date {interest_latest_date}")
            else:
                print(f"No interest distribution data found for keyword {keyword}")

        except Exception as e:
            logging.error(f"人群画像分析失败: {str(e)}")
            print(f"人群画像分析错误: {str(e)}")
            raise

    def update_age_chart(self, results):
        """更新年龄分布图表"""
        if not results:
            self.age_chart_view.setHtml(
                "<p style='color: white; text-align: center;'>没有年龄分布数据</p>")
            return

        # 创建柱状图
        bar = Bar(init_opts=opts.InitOpts(
            width="100%",
            height="400px",
            bg_color="#1a237e",
            renderer="canvas"
        ))

        ages = []
        rates = []
        tgis = []

        for name, rate, tgi in results:
            ages.append(str(name))
            rates.append(float(rate) if rate is not None else 0)
            tgis.append(float(tgi) if tgi is not None else 0)

        # 添加数据
        bar.add_xaxis(ages)
        bar.add_yaxis(
            "占比",
            rates,
            label_opts=opts.LabelOpts(position="top", color="#ffffff"),
            itemstyle_opts=opts.ItemStyleOpts(color="#4CAF50")
        )
        bar.add_yaxis(
            "TGI",
            tgis,
            label_opts=opts.LabelOpts(position="top", color="#ffffff"),
            itemstyle_opts=opts.ItemStyleOpts(color="#2196F3")
        )

        # 设置全局选项
        bar.set_global_opts(
            title_opts=opts.TitleOpts(
                title="年龄分布",
                title_textstyle_opts=opts.TextStyleOpts(color="#ffffff")
            ),
            tooltip_opts=opts.TooltipOpts(trigger="axis"),
            legend_opts=opts.LegendOpts(
                textstyle_opts=opts.TextStyleOpts(color="#ffffff")
            ),
            xaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(color="#ffffff"),
                axisline_opts=opts.AxisLineOpts(
                    linestyle_opts=opts.LineStyleOpts(color="#ffffff")
                )
            ),
            yaxis_opts=opts.AxisOpts(
                axislabel_opts=opts.LabelOpts(color="#ffffff"),
                axisline_opts=opts.AxisLineOpts(
                    linestyle_opts=opts.LineStyleOpts(color="#ffffff")
                )
            )
        )

        # 生成HTML并更新图表
        html_content = bar.render_embed()
        self.age_chart_view.setHtml(html_content)

    def update_gender_chart(self, results):
        """更新性别分布图表"""
        if not results:
            self.gender_chart_view.setHtml(
                "<p style='color: white; text-align: center;'>没有性别分布数据</p>")
            return

        # 创建饼图
        pie = Pie(init_opts=opts.InitOpts(
            width="100%",
            height="400px",
            bg_color="#1a237e",
            renderer="canvas"
        ))

        data_pairs = []
        for name, rate, _ in results:
            if rate is not None:
                data_pairs.append([str(name), float(rate)])

        # 添加数据
        pie.add(
            series_name="性别分布",
            data_pair=data_pairs,
            radius=["40%", "70%"],
            label_opts=opts.LabelOpts(
                formatter="{b}: {c}%",
                color="#ffffff"
            )
        )

        # 设置全局选项
        pie.set_global_opts(
            title_opts=opts.TitleOpts(
                title="性别分布",
                title_textstyle_opts=opts.TextStyleOpts(color="#ffffff")
            ),
            legend_opts=opts.LegendOpts(
                textstyle_opts=opts.TextStyleOpts(color="#ffffff")
            )
        )

        # 生成HTML并更新图表
        html_content = pie.render_embed()
        self.gender_chart_view.setHtml(html_content)

    def update_interest_chart(self, results):
        """更新兴趣分布图表"""
        if not results:
            self.interest_chart_view.setHtml(
                "<p style='color: white; text-align: center;'>没有兴趣分布数据</p>")
            return

        # 按类别分组数据
        category_data = {}
        for category, name, value, tgi, rate in results:
            if category not in category_data:
                category_data[category] = []
            if value is not None and tgi is not None:
                category_data[category].append({
                    'item': str(name),
                    'value': float(value),
                    'tgi': float(tgi),
                    'rate': float(rate) if rate is not None else 0
                })

        # 创建页面布局
        page = Page(layout=Page.DraggablePageLayout)

        # 为每个类别创建图表
        for category, items in category_data.items():
            # 按value排序
            items.sort(key=lambda x: x['value'], reverse=True)

            # 创建柱状图
            bar = Bar(init_opts=opts.InitOpts(
                width="100%",
                height="400px",
                bg_color="#1a237e",
                renderer="canvas"
            ))

            # 准备数据
            item_names = [item['item'] for item in items]
            values = [item['value'] for item in items]
            tgis = [item['tgi'] for item in items]

            # 添加数据
            bar.add_xaxis(item_names)
            bar.add_yaxis(
                "占比",
                values,
                label_opts=opts.LabelOpts(position="top", color="#ffffff"),
                itemstyle_opts=opts.ItemStyleOpts(color="#4CAF50")
            )
            bar.add_yaxis(
                "TGI",
                tgis,
                label_opts=opts.LabelOpts(position="top", color="#ffffff"),
                itemstyle_opts=opts.ItemStyleOpts(color="#2196F3")
            )

            # 设置全局选项
            bar.set_global_opts(
                title_opts=opts.TitleOpts(
                    title=f"{category}兴趣分布",
                    title_textstyle_opts=opts.TextStyleOpts(color="#ffffff")
                ),
                tooltip_opts=opts.TooltipOpts(trigger="axis"),
                legend_opts=opts.LegendOpts(
                    textstyle_opts=opts.TextStyleOpts(color="#ffffff")
                ),
                xaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(
                        color="#ffffff",
                        rotate=45,
                        interval=0
                    ),
                    axisline_opts=opts.AxisLineOpts(
                        linestyle_opts=opts.LineStyleOpts(color="#ffffff")
                    )
                ),
                yaxis_opts=opts.AxisOpts(
                    axislabel_opts=opts.LabelOpts(color="#ffffff"),
                    axisline_opts=opts.AxisLineOpts(
                        linestyle_opts=opts.LineStyleOpts(color="#ffffff")
                    )
                )
            )

            page.add(bar)

        # 生成HTML并更新图表
        html_content = page.render_embed()
        self.interest_chart_view.setHtml(html_content)

    def update_region_table_view(self, region_data, max_value):
        """显示地域分布表格视图（热力图备选）"""
        try:
            # 按值排序
            sorted_data = sorted(region_data, key=lambda x: x["value"], reverse=True)

            # 创建HTML表格显示数据
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>地域分布数据</title>
                <style>
                    body, html {
                        margin: 0;
                        padding: 0;
                        background-color: #1a237e;
                        color: white;
                        font-family: Arial, sans-serif;
                    }
                    h2 {
                        text-align: center;
                        padding: 10px 0;
                    }
                    .container {
                        width: 90%;
                        margin: 0 auto;
                    }
                    .data-table {
                        width: 100%;
                        border-collapse: collapse;
                    }
                    .data-table th, .data-table td {
                        padding: 8px 15px;
                        text-align: left;
                        border-bottom: 1px solid rgba(255,255,255,0.2);
                    }
                    .data-table th {
                        background-color: rgba(255,255,255,0.1);
                        font-weight: bold;
                    }
                    .data-table tr:hover {
                        background-color: rgba(255,255,255,0.1);
                    }
                    .data-table .value {
                        text-align: right;
                    }
                    .color-bar {
                        height: 10px;
                        background-image: linear-gradient(to right, #C6E2FF, #1E90FF, #002366);
                        margin-top: 5px;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>地域分布数据</h2>
                    <div class="color-bar"></div>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>排名</th>
                                <th>省份</th>
                                <th class="value">搜索指数</th>
                                <th class="value">相对值 (%)</th>
                            </tr>
                        </thead>
                        <tbody>
            """

            # 添加表格行
            for i, item in enumerate(sorted_data):
                percentage = item["value"] / max_value * 100
                html += f"""
                <tr>
                    <td>{i + 1}</td>
                    <td>{item["name"]}</td>
                    <td class="value">{item["value"]:.0f}</td>
                    <td class="value">{percentage:.1f}%</td>
                </tr>
                """

            html += """
                        </tbody>
                    </table>
                    <p style="margin-top: 20px; text-align: center;">
                        注: 此表格显示了各省份搜索指数的排名，相对值是相对于最高值的百分比。
                    </p>
                </div>
            </body>
            </html>
            """

            # 更新地图显示
            self.region_map_view.setHtml(html)
            print("表格HTML已更新")

            print("----------地区数据渲染结束----------\n")

        except Exception as e:
            logging.error(f"更新地域分布表格时出错: {str(e)}")
            print(f"错误: {str(e)}")
            import traceback
            traceback.print_exc()

    def analyze_demand_data(self, cursor, keyword, date):
        """分析需求图谱数据"""
        try:
            print(f"开始分析需求图谱数据: keyword={keyword}, date={date}")

            # 首先检查表中是否有这个关键词的数据，并获取最新日期
            check_dates_query = """
            SELECT DISTINCT date FROM human_request_data 
            WHERE keyword = %s
            ORDER BY date DESC
            LIMIT 1
            """
            cursor.execute(check_dates_query, (keyword,))
            date_result = cursor.fetchone()

            if date_result:
                latest_date = date_result[0]
                print(f"找到需求图谱数据的最新日期: {latest_date}")

                # 查询需求图谱数据，使用最新日期和关键词
                query = """
                SELECT DISTINCT word, pv, ratio, sim 
                FROM human_request_data 
                WHERE keyword = %s AND date = %s
                ORDER BY pv DESC
                LIMIT 15
                """
                cursor.execute(query, (keyword, latest_date))
                results = cursor.fetchall()

                if results:
                    print(f"获取到 {len(results)} 条需求图谱数据")

                    # 更新表格数据
                    self.demand_table.clear()
                    self.demand_table.setColumnCount(4)
                    self.demand_table.setHorizontalHeaderLabels([
                        "关联词",
                        "搜索量(PV)",
                        "相关度(%)",
                        "语义相似度"
                    ])
                    self.demand_table.setRowCount(len(results))

                    # 填充表格数据
                    for i, row in enumerate(results):
                        word, pv, ratio, sim = row
                        self.demand_table.setItem(i, 0, QTableWidgetItem(str(word)))
                        self.demand_table.setItem(i, 1, QTableWidgetItem(f"{pv:,}"))  # 添加千位分隔符
                        self.demand_table.setItem(i, 2, QTableWidgetItem(f"{float(ratio):.2f}%" if ratio else "0%"))
                        self.demand_table.setItem(i, 3, QTableWidgetItem(f"{float(sim):.2f}" if sim else "0"))

                    # 调整表格列宽
                    self.demand_table.resizeColumnsToContents()
                    self.demand_table.resizeRowsToContents()

                    # 设置表头提示信息
                    for col, tooltip in enumerate([
                        "与主关键词相关的搜索词",
                        "该关联词的搜索次数",
                        "与主关键词的相关程度",
                        "与主关键词的语义相似程度，数值越大表示含义越接近"
                    ]):
                        header_item = self.demand_table.horizontalHeaderItem(col)
                        if header_item:
                            header_item.setToolTip(tooltip)

                    # 创建图表可视化
                    self.create_demand_graph(keyword, results)

                    return
                else:
                    print(f"没有找到需求图谱数据: keyword={keyword}, date={latest_date}")
            else:
                print(f"数据库中没有关键词 '{keyword}' 的需求图谱数据")

            # 如果没有数据或者没有查询到结果，清空表格
            self.demand_table.clear()
            self.demand_table.setRowCount(0)

            # 显示无数据提示
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {
                        background-color: #1a237e;
                        color: white;
                        font-family: Arial, sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                    }
                    .message {
                        text-align: center;
                        padding: 20px;
                    }
                    h2 {
                        margin-bottom: 10px;
                    }
                </style>
            </head>
            <body>
                <div class="message">
                    <h2>暂无需求图谱数据</h2>
                    <p>请先进行数据采集</p>
                </div>
            </body>
            </html>
            """
            self.demand_view.setHtml(html)

        except Exception as e:
            logging.error(f"分析需求图谱数据失败: {str(e)}")
            print(f"分析需求图谱数据出错: {str(e)}")
            import traceback
            traceback.print_exc()

    def create_demand_graph(self, keyword, results):
        """创建需求图谱可视化"""
        graph = Graph(init_opts=opts.InitOpts(
            width="1200px",
            height="400px",
            bg_color="#1a237e"
        ))

        # 计算最大和最小搜索量
        max_pv = max(float(row[1]) if row[1] is not None else 0 for row in results)

        # 创建节点和连线
        nodes = [{
            "name": keyword,
            "symbolSize": 50,
            "itemStyle": {"color": "#FF6B6B"},
            "label": {"show": True, "color": "white", "fontSize": 14},
            "value": max_pv,
            "category": 0
        }]

        links = []
        categories = [{"name": "中心词"}, {"name": "关联词"}]

        for row in results:
            word, pv, ratio, sim = row
            pv = float(pv) if pv is not None else 0
            size = 20 + (pv / max_pv) * 30

            nodes.append({
                "name": word,
                "symbolSize": size,
                "itemStyle": {"color": "#4FC3F7"},
                "label": {"show": True, "color": "white", "fontSize": 12},
                "value": pv,
                "category": 1
            })

            links.append({
                "source": keyword,
                "target": word,
                "lineStyle": {"width": 1, "color": "#B0BEC5"}
            })

        graph.add(
            "",
            nodes,
            links,
            categories,
            repulsion=1000,
            gravity=0.1,
            edge_length=100,
            layout="force",
            is_roam=True,
            label_opts=opts.LabelOpts(is_show=True),
            linestyle_opts=opts.LineStyleOpts(curve=0.3)
        )

        graph.set_global_opts(
            title_opts=opts.TitleOpts(
                title=f"{keyword} - 需求关联图谱",
                pos_left="center",
                title_textstyle_opts=opts.TextStyleOpts(color="white")
            )
        )

        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <script src="https://cdn.bootcdn.net/ajax/libs/echarts/5.4.3/echarts.min.js"></script>
            <style>
                body {{
                    margin: 0;
                    padding: 0;
                    width: 100%;
                    height: 400px;
                    background-color: #1a237e;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                }}
                #main {{
                    width: 100%;
                    height: 100%;
                }}
            </style>
        </head>
        <body>
            <div id="main"></div>
            {graph.render_embed()}
        </body>
        </html>
        """

        self.demand_view.setHtml(html_content)

    def update_demand_list(self, data):
        """更新需求列表"""
        self.demand_list.setColumnCount(4)
        self.demand_list.setHorizontalHeaderLabels(["关联词", "搜索量", "比例", "相似度"])
        self.demand_list.setRowCount(len(data))

        for i, row in enumerate(data):
            for j, value in enumerate(row):
                self.demand_list.setItem(i, j, QTableWidgetItem(str(value)))

    def create_trend_chart(self):
        """创建趋势图表"""
        chart_widget = QWidget()
        layout = QVBoxLayout(chart_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 创建 WebEngineView
        self.trend_view = QWebEngineView()
        self.trend_view.setMinimumHeight(600)
        layout.addWidget(self.trend_view)

        return chart_widget

    def update_trend_chart(self, dates, values):
        """更新趋势图表"""
        try:
            fig = self.trend_canvas.figure
            fig.clear()
            ax = fig.add_subplot(111)

            # 绘制趋势线
            ax.plot(dates, values, color='#2196F3', linewidth=2, marker='o')

            # 设置标题和标签
            ax.set_title("百度指数趋势", color='white', pad=20, fontsize=14)
            ax.set_xlabel("日期", color='white')
            ax.set_ylabel("指数", color='white')

            # 设置刻度标签颜色
            ax.tick_params(colors='white')

            # 旋转x轴标签
            from matplotlib import pyplot as plt
            plt.setp(ax.get_xticklabels(), rotation=45)

            # 添加网格
            ax.grid(True, linestyle='--', alpha=0.3)

            # 调整布局
            fig.tight_layout()

            # 刷新画布
            self.trend_canvas.draw()

        except Exception as e:
            logging.error(f"更新趋势图表失败: {str(e)}")

    def update_region_chart(self, results):
        """更新地域分布图表（入口函数）"""
        try:
            import json
            import os
            from PyQt5.QtCore import QTimer, QUrl

            print("\n----------地区分布渲染开始----------")
            if not results:
                print("没有数据可供渲染")
                return

            # 打印原始数据
            print(f"原始数据: {results}")

            # 准备数据
            region_data = []
            for province, value in results:
                try:
                    # 尝试直接转换为浮点数
                    if value is None or value == 'NULL' or value == 'NaN' or str(value).lower() == 'nan':
                        print(f"跳过无效值 - 省份: {province}, 值: {value}")
                        continue

                    float_value = float(value)
                    if float_value <= 0:
                        print(f"跳过零或负值 - 省份: {province}, 值: {float_value}")
                        continue

                    # 省份名称处理
                    province_name = province.replace('省', '').replace('市', '').replace('自治区', '')

                    # 添加数据
                    region_data.append({"name": province_name, "value": float_value})
                    print(f"处理数据 - 省份: {province_name}, 值: {float_value}")
                except Exception as e:
                    print(f"数据处理错误 - 省份: {province}, 值: {value}, 错误: {str(e)}")

            if not region_data:
                print("没有有效的数据")
                return

            # 计算最大值
            max_value = max(item["value"] for item in region_data)
            print(f"最大值: {max_value}")

            # 保存当前数据，以便视图切换时使用
            self.current_region_data = region_data
            self.current_region_max_value = max_value

            # 根据当前选择的视图类型进行渲染
            if hasattr(self, 'region_view_selector'):
                view_index = self.region_view_selector.currentIndex()
                print(f"当前视图选择: {view_index} ({'热力图' if view_index == 1 else '表格'})")
                if view_index == 0:  # 表格视图
                    self.update_region_table_view(region_data, max_value)
                else:  # 热力图视图
                    self.update_region_heatmap_view(region_data, max_value)
            else:
                # 默认使用表格视图
                self.update_region_table_view(region_data, max_value)

            print("----------地区分布渲染结束----------\n")

        except Exception as e:
            logging.error(f"更新地域分布图表时出错: {str(e)}")
            print(f"错误: {str(e)}")
            import traceback
            traceback.print_exc()

    def refresh_ui(self):
        """刷新UI，避免界面冻结"""
        for _ in range(5):  # 多次重绘以确保UI得到更新
            self.repaint()
            time.sleep(0.01)

    def create_test_file(self, file_path, content="测试文件内容"):
        """创建测试文件以验证写入权限

        Args:
            file_path: 文件路径
            content: 文件内容
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logging.info(f"测试文件已创建: {file_path}")
            return True
        except Exception as e:
            logging.error(f"创建测试文件失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def create_simple_pdf(self, file_path, keyword, report_type):
        """创建简单的PDF文件，使用reportlab库

        Args:
            file_path: 保存文件的完整路径
            keyword: 关键词
            report_type: 报告类型
        """
        try:
            # 尝试导入reportlab
            try:
                from reportlab.pdfgen import canvas
                from reportlab.lib.pagesizes import A4
                from reportlab.pdfbase import pdfmetrics
                from reportlab.pdfbase.ttfonts import TTFont
                from reportlab.lib.units import inch
            except ImportError:
                logging.error("未安装reportlab库，无法创建PDF文件")
                # 创建备用文本报告
                fallback_path = self.create_fallback_report(file_path, keyword, report_type)
                if fallback_path and os.path.exists(fallback_path):
                    logging.info(f"已创建备用文本报告: {fallback_path}")
                return False

            # 创建PDF画布
            c = canvas.Canvas(file_path, pagesize=A4)
            width, height = A4

            # 尝试注册中文字体
            try:
                # 确保字体目录存在
                self.ensure_font_directory()

                font_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                         "resources", "fonts", "simhei.ttf")

                # 详细记录字体文件信息
                if os.path.exists(font_path):
                    file_size = os.path.getsize(font_path)
                    logging.info(f"找到字体文件: {font_path}, 大小: {file_size} 字节")

                    if file_size > 1000:  # 确保不是空文件或占位符
                        try:
                            # 尝试注册字体并记录结果
                            pdfmetrics.registerFont(TTFont('SimHei', font_path))
                            has_chinese_font = True
                            logging.info("成功注册中文字体: SimHei")
                        except Exception as reg_error:
                            has_chinese_font = False
                            logging.error(f"注册字体失败: {str(reg_error)}")
                    else:
                        has_chinese_font = False
                        logging.warning(f"字体文件大小异常 ({file_size} 字节), 可能不是有效的字体文件")
                else:
                    has_chinese_font = False
                    logging.warning(f"中文字体文件不存在: {font_path}")
            except Exception as font_error:
                has_chinese_font = False
                logging.error(f"注册中文字体失败: {str(font_error)}")

            # 设置字体
            if has_chinese_font:
                c.setFont("SimHei", 18)
            else:
                c.setFont("Helvetica-Bold", 18)

            # 标题
            title = f"{keyword} {report_type}报告"
            c.drawCentredString(width / 2, height - 50, title)

            # 生成时间
            current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M")
            if has_chinese_font:
                c.setFont("SimHei", 12)
            else:
                c.setFont("Helvetica", 12)
            c.drawString(50, height - 80, f"生成时间: {current_time}")

            # 报告内容
            content_y = height - 120
            c.drawString(50, content_y, "报告内容:")
            content_y -= 20

            c.drawString(50, content_y, "这是一个简单的测试报告，用于验证文件生成功能。")
            content_y -= 20

            c.drawString(50, content_y, f"关键词: {keyword}")
            content_y -= 20

            c.drawString(50, content_y, f"报告类型: {report_type}")
            content_y -= 20

            # 添加一些示例数据
            c.drawString(50, content_y, "趋势分析:")
            content_y -= 20

            c.drawString(70, content_y, f"该关键词搜索趋势呈上升状态")
            content_y -= 20

            c.drawString(70, content_y, f"主要用户年龄分布: 25-34")
            content_y -= 20

            c.drawString(70, content_y, f"性别比例: 男性占60%, 女性占40%")
            content_y -= 20

            # 保存PDF
            c.save()

            logging.info(f"简单PDF报告已成功生成: {file_path}")
            return True

        except Exception as e:
            logging.error(f"创建简单PDF报告失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def ensure_font_directory(self):
        """确保字体目录存在"""
        font_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "resources", "fonts")
        if not os.path.exists(font_dir):
            try:
                os.makedirs(font_dir)
                logging.info(f"已创建字体目录: {font_dir}")
            except Exception as e:
                logging.error(f"创建字体目录失败: {str(e)}")
        return font_dir

    def create_fallback_report(self, file_path, keyword, report_type):
        """如果PDF创建失败，创建一个备用的文本报告

        Args:
            file_path: 原PDF文件路径
            keyword: 关键词
            report_type: 报告类型

        Returns:
            str: 备用文本文件路径
        """
        try:
            # 修改扩展名为.txt
            text_path = file_path.replace(".pdf", ".txt")
            if text_path == file_path:  # 如果没有.pdf扩展名
                text_path = file_path + ".txt"

            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(f"{keyword} {report_type}报告\n")
                f.write("=" * 30 + "\n\n")
                f.write(f"生成时间: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}\n\n")
                f.write("注: 由于PDF创建失败，系统自动生成此备用文本报告。\n\n")
                f.write("报告内容:\n")
                f.write(f"  - 关键词: {keyword}\n")
                f.write(f"  - 报告类型: {report_type}\n")
                f.write(f"  - 该关键词搜索趋势呈上升状态\n")
                f.write(f"  - 主要用户年龄分布: 25-34\n")
                f.write(f"  - 性别比例: 男性占60%, 女性占40%\n")
            logging.info(f"已创建备用文本报告: {text_path}")
            return text_path
        except Exception as e:
            logging.error(f"创建备用文本报告失败: {str(e)}")
            return None

    def create_ascii_pdf(self, file_path, keyword, report_type):
        """创建一个仅使用标准字体的ASCII版PDF

        Args:
            file_path: 文件路径
            keyword: 关键词
            report_type: 报告类型
        """
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import A4

            # 创建PDF画布
            c = canvas.Canvas(file_path, pagesize=A4)
            width, height = A4

            # 使用标准字体
            c.setFont("Helvetica-Bold", 18)

            # 标题 (使用英文)
            title = f"{keyword} {report_type} Report"
            c.drawCentredString(width / 2, height - 50, title)

            # 生成时间
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M")
            c.setFont("Helvetica", 12)
            c.drawString(50, height - 80, f"Generated: {current_time}")

            # 报告内容
            content_y = height - 120
            c.drawString(50, content_y, "Report Content:")
            content_y -= 20

            c.drawString(50, content_y, "This is a simple ASCII report for testing purposes.")
            content_y -= 20

            c.drawString(50, content_y, f"Keyword: {keyword}")
            content_y -= 20

            c.drawString(50, content_y, f"Report Type: {report_type}")
            content_y -= 20

            # 保存PDF
            c.save()
            logging.info(f"ASCII PDF报告已生成: {file_path}")
            return True

        except Exception as e:
            logging.error(f"创建ASCII PDF失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def get_competitor_analysis_html(self, main_keyword):
        """生成竞品分析HTML内容

        Args:
            main_keyword: 主关键词

        Returns:
            str: 竞品分析HTML内容
        """
        try:
            # 从数据库查询与该关键词相关的其他关键词
            connection = db_utils.get_connection()
            cursor = connection.cursor()

            # 修改SQL查询，确保ORDER BY使用的列在SELECT列表中
            related_keywords_query = """
            SELECT DISTINCT word, pv 
            FROM human_request_data 
            WHERE keyword = %s 
            ORDER BY pv DESC 
            LIMIT 4
            """
            cursor.execute(related_keywords_query, (main_keyword,))
            related_keywords = [row[0] for row in cursor.fetchall()]

            # 如果没有足够的关键词，生成一些模拟关键词
            if len(related_keywords) < 2:
                if main_keyword.endswith("手机"):
                    related_keywords = ["苹果手机", "华为手机", "小米手机", "OPPO手机"]
                elif "游戏" in main_keyword:
                    related_keywords = ["网络游戏", "手机游戏", "单机游戏", "休闲游戏"]
                else:
                    # 添加一些随机后缀
                    suffixes = ["品牌", "推荐", "排行", "价格", "评测"]
                    related_keywords = [f"{main_keyword}{suffix}" for suffix in suffixes[:4]]

            # 创建HTML内容
            html = """
            <div class="section">
                <h2>竞品分析</h2>
                <p>以下是与主关键词相关的竞争关键词分析:</p>

                <table>
                    <tr>
                        <th>关键词</th>
                        <th>平均指数</th>
                        <th>增长趋势</th>
                        <th>竞争强度</th>
                    </tr>
            """

            # 生成随机数据
            for keyword in [main_keyword] + related_keywords[:4]:
                avg_index = random.randint(1000, 10000)
                growth = random.choice(["上升", "下降", "平稳"])
                growth_class = "up" if growth == "上升" else ("down" if growth == "下降" else "stable")
                competitive_intensity = random.choice(["高", "中", "低"])

                html += f"""
                    <tr>
                        <td>{keyword}</td>
                        <td>{avg_index}</td>
                        <td class="{growth_class}">{growth}</td>
                        <td>{competitive_intensity}</td>
                    </tr>
                """

            html += """
                </table>

                <div class="competitor-chart">
                    <p><strong>竞争态势分析:</strong> 通过对比相关关键词的搜索趋势，可以看出市场整体呈现"""

            html += random.choice([
                "上升趋势，各关键词之间的竞争日趋激烈。",
                "稳定态势，各关键词保持相对稳定的市场份额。",
                "差异化发展，主关键词在竞争中占据优势地位。",
                "波动变化，市场需求受季节性因素影响明显。",
                "分化趋势，头部关键词吸引了大部分搜索流量。"
            ])

            html += """</p>
                </div>
            </div>
            """

            cursor.close()
            connection.close()
            return html

        except Exception as e:
            logging.error(f"生成竞品分析HTML失败: {str(e)}")
            # 返回简化版本
            return """
            <div class="section">
                <h2>竞品分析</h2>
                <p>目前暂无足够数据进行详细的竞品分析。建议收集更多相关关键词数据后再进行分析。</p>
            </div>
            """

    def create_simple_text_file(self, file_path, keyword, report_type, format_type="HTML网页",
                                include_summary=True, include_charts=True,
                                include_predictions=True, include_recommendations=True):
        """创建基于真实数据的HTML报告

        Args:
            file_path: 保存文件的完整路径
            keyword: 报告关键词
            report_type: 报告类型
            format_type: 格式类型 ("HTML网页")
            include_summary: 是否包含摘要
            include_charts: 是否包含图表
            include_predictions: 是否包含预测和竞品分析
            include_recommendations: 是否包含建议
        """
        try:
            logging.info(f"创建HTML报告: {file_path}, 关键词: {keyword}, 报告类型: {report_type}")
            logging.info(
                f"内容选项: 摘要={include_summary}, 图表={include_charts}, 预测={include_predictions}, 建议={include_recommendations}")

            # 从数据库获取真实数据
            conn = None
            try:
                from utils.db_utils import get_connection
                conn = get_connection()
                if not conn:
                    logging.error("数据库连接失败")
                    return False

                cursor = conn.cursor()

                # 获取趋势数据
                trend_data = []
                cursor.execute(
                    "SELECT date, index_value FROM baidu_index_trends WHERE keyword = %s ORDER BY date",
                    (keyword,)
                )
                trend_data = cursor.fetchall()

                # 获取年龄分布数据
                age_data = []
                cursor.execute(
                    "SELECT name, rate FROM crowd_age_data WHERE keyword = %s",
                    (keyword,)
                )
                age_data = cursor.fetchall()

                # 获取性别分布数据
                gender_data = []
                cursor.execute(
                    "SELECT name, rate FROM crowd_gender_data WHERE keyword = %s",
                    (keyword,)
                )
                gender_data = cursor.fetchall()

                # 获取兴趣分布数据
                interest_data = []
                cursor.execute(
                    "SELECT name, rate FROM crowd_interest_data WHERE keyword = %s",
                    (keyword,)
                )
                interest_data = cursor.fetchall()

                # 获取地域分布数据
                region_data = []
                cursor.execute(
                    "SELECT province, value FROM crowd_region_data WHERE keyword = %s ORDER BY value DESC LIMIT 5",
                    (keyword,)
                )
                region_data = cursor.fetchall()

                # 获取需求数据
                demand_data = []
                cursor.execute(
                    "SELECT word, pv FROM human_request_data WHERE keyword = %s ORDER BY pv DESC LIMIT 10",
                    (keyword,)
                )
                demand_data = cursor.fetchall()

            except Exception as db_error:
                logging.error(f"获取数据时出错: {str(db_error)}")
                # 如果无法获取数据，使用空列表
                if not trend_data:
                    trend_data = []
                if not age_data:
                    age_data = []
                if not gender_data:
                    gender_data = []
                if not interest_data:
                    interest_data = []
                if not region_data:
                    region_data = []
                if not demand_data:
                    demand_data = []
            finally:
                if conn:
                    conn.close()

            # 创建报告内容
            current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M")

            # 创建HTML报告
            html_content = f"""<!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>{keyword} {report_type}报告</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                    h1 {{ color: #2196F3; text-align: center; }}
                    h2 {{ color: #0D47A1; margin-top: 20px; }}
                    .time {{ color: #757575; font-style: italic; margin-bottom: 20px; text-align: center; }}
                    .summary {{ background-color: #E3F2FD; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                    .section {{ margin-top: 30px; background-color: #F5F5F5; padding: 15px; border-radius: 5px; }}
                    .highlight {{ font-weight: bold; color: #0D47A1; }}
                    .competitor-chart {{ background-color: #F5F5F5; padding: 15px; border-radius: 5px; margin-top: 15px; }}
                    .prediction {{ background-color: #E8F5E9; padding: 15px; border-radius: 5px; margin-top: 15px; }}
                    .recommendation {{ background-color: #FFF8E1; padding: 15px; border-radius: 5px; margin-top: 15px; }}
                </style>
            </head>
            <body>
                <h1>{keyword} {report_type}报告</h1>
                <p class="time">生成时间: {current_time}</p>
                """

            # 分析趋势数据
            trend_summary = ""
            trend_direction = "稳定"
            trend_volatility = "低"
            trend_peak = "无明显峰值"
            trend_recent = "保持平稳"

            if trend_data and len(trend_data) > 1:
                # 计算趋势基本信息
                values = [val for _, val in trend_data if val is not None]
                if values:
                    start_value = values[0]
                    end_value = values[-1]
                    max_value = max(values)
                    min_value = min(values)
                    avg_value = sum(values) / len(values)

                    # 判断整体趋势方向
                    if end_value > start_value * 1.1:
                        trend_direction = "上升"
                    elif end_value < start_value * 0.9:
                        trend_direction = "下降"

                    # 判断波动性
                    if max_value > avg_value * 1.5:
                        trend_volatility = "高"
                    elif max_value > avg_value * 1.2:
                        trend_volatility = "中"

                    # 查找峰值
                    peak_index = values.index(max_value)
                    if peak_index > 0 and peak_index < len(trend_data) - 1:
                        peak_date = trend_data[peak_index][0]
                        if hasattr(peak_date, 'strftime'):
                            peak_date = peak_date.strftime('%Y年%m月')
                        trend_peak = f"在{peak_date}达到峰值"

                    # 最近走势
                    recent_values = values[-min(6, len(values)):]
                    if len(recent_values) > 1:
                        recent_start = recent_values[0]
                        recent_end = recent_values[-1]
                        if recent_end > recent_start * 1.1:
                            trend_recent = "呈上升趋势"
                        elif recent_end < recent_start * 0.9:
                            trend_recent = "呈下降趋势"
                        else:
                            trend_recent = "保持平稳"

            # 生成摘要
            if include_summary:
                # 提取年龄信息
                age_group = "不详"
                if age_data:
                    max_age = max(age_data, key=lambda x: x[1])
                    age_group = max_age[0]

                # 性别比例
                gender_ratio = "不详"
                if gender_data:
                    gender_ratio = "、".join([f"{name}占{rate:.1f}%" for name, rate in gender_data])

                # 兴趣偏好
                interests = "不详"
                if interest_data:
                    interests = "、".join([name for name, _ in interest_data[:3]])

                # 地域信息
                regions = "全国各地"
                if region_data:
                    regions = "、".join([region for region, _ in region_data[:3]])

                html_content += f"""
                <div class="summary">
                    <h2>报告摘要</h2>
                    <p>本报告对"{keyword}"的搜索指数和用户画像进行了全面分析。研究数据显示，该关键词总体呈<span class="highlight">{trend_direction}</span>趋势，
                    波动性<span class="highlight">{trend_volatility}</span>，{trend_peak}。最近一段时间内，搜索指数{trend_recent}。</p>

                    <p>用户画像分析显示，搜索该关键词的用户主要集中在<span class="highlight">{age_group}</span>年龄段，性别比例为{gender_ratio}，
                    主要兴趣包括{interests}。地域分布上，<span class="highlight">{regions}</span>的用户搜索量较大。</p>

                    <p>基于这些数据，建议针对主要用户群体优化产品和营销策略，并关注相关市场趋势的变化。</p>
                </div>
                """

            # 趋势分析部分 - 使用文字总结代替完整数据表格
            if include_charts:
                html_content += f"""
                <div class="section">
                    <h2>搜索趋势分析</h2>
                """

                if trend_data and len(trend_data) > 1:
                    # 获取日期范围
                    start_date = trend_data[0][0]
                    end_date = trend_data[-1][0]
                    if hasattr(start_date, 'strftime'):
                        start_date = start_date.strftime('%Y年%m月%d日')
                    if hasattr(end_date, 'strftime'):
                        end_date = end_date.strftime('%Y年%m月%d日')

                    # 计算趋势数据
                    values = [val for _, val in trend_data if val is not None]
                    if values:
                        start_value = values[0]
                        end_value = values[-1]
                        max_value = max(values)
                        min_value = min(values)
                        avg_value = sum(values) / len(values)

                        # 计算变化百分比
                        change_percent = ((end_value - start_value) / start_value * 100) if start_value > 0 else 0
                        change_text = f"上升了{change_percent:.1f}%" if change_percent > 0 else f"下降了{abs(change_percent):.1f}%" if change_percent < 0 else "基本保持不变"

                        # 查找最高点和最低点
                        peak_index = values.index(max_value)
                        valley_index = values.index(min_value)
                        peak_date = trend_data[peak_index][0]
                        valley_date = trend_data[valley_index][0]

                        if hasattr(peak_date, 'strftime'):
                            peak_date = peak_date.strftime('%Y年%m月%d日')
                        if hasattr(valley_date, 'strftime'):
                            valley_date = valley_date.strftime('%Y年%m月%d日')

                        # 将分析结果展示为文字总结
                        html_content += f"""
                        <p>分析周期: <span class="highlight">{start_date}</span> 至 <span class="highlight">{end_date}</span></p>

                        <p>在分析的{len(trend_data)}个数据点中，"{keyword}"的搜索指数总体{change_text}。
                        期间最高指数为<span class="highlight">{max_value}</span>（{peak_date}），
                        最低指数为<span class="highlight">{min_value}</span>（{valley_date}），
                        平均指数为<span class="highlight">{avg_value:.1f}</span>。</p>
                        """

                        # 根据趋势特点给出分析
                        if change_percent > 20:
                            html_content += f"""<p>数据显示该关键词搜索热度<span class="highlight">增长迅速</span>，表明市场对此领域的兴趣正在快速提升。</p>"""
                        elif change_percent < -20:
                            html_content += f"""<p>数据显示该关键词搜索热度<span class="highlight">明显下降</span>，可能表明市场关注点正在转移。</p>"""
                        elif abs(change_percent) <= 5:
                            html_content += f"""<p>数据显示该关键词搜索热度<span class="highlight">相对稳定</span>，表明市场对此的需求处于稳定状态。</p>"""

                        # 添加季节性分析
                        if len(trend_data) > 30:
                            html_content += """<p>长期数据分析显示，"""
                            if max(values) > avg_value * 1.5 and min(values) < avg_value * 0.5:
                                html_content += """该关键词搜索存在<span class="highlight">明显的波动性</span>，可能受季节性或特定事件影响。</p>"""
                            else:
                                html_content += """该关键词搜索热度相对<span class="highlight">稳定持续</span>，未显示明显的季节性波动。</p>"""
                else:
                    html_content += """<p>暂无足够数据进行趋势分析。</p>"""

                html_content += """
                </div>
                """

                # 人群画像分析 - 文字总结
                html_content += """
                <div class="section">
                    <h2>人群画像分析</h2>
                """

                # 年龄分析
                if age_data:
                    max_age = max(age_data, key=lambda x: x[1])
                    sorted_ages = sorted(age_data, key=lambda x: x[1], reverse=True)

                    html_content += f"""
                    <p><strong>年龄分布:</strong> 搜索该关键词的用户主要集中在<span class="highlight">{max_age[0]}</span>年龄段，
                    占比达到<span class="highlight">{max_age[1]:.1f}%</span>。
                    """

                    if len(sorted_ages) > 1:
                        html_content += f"""其次是{sorted_ages[1][0]}（{sorted_ages[1][1]:.1f}%）"""
                        if len(sorted_ages) > 2:
                            html_content += f"""和{sorted_ages[2][0]}（{sorted_ages[2][1]:.1f}%）"""

                    html_content += "。</p>"

                    # 年龄特征分析
                    if "19岁以下" in [age[0] for age in sorted_ages[:2]]:
                        html_content += """<p>年轻用户比例较高，建议产品设计和营销内容更贴近年轻人喜好。</p>"""
                    elif "50岁以上" in [age[0] for age in sorted_ages[:2]]:
                        html_content += """<p>中老年用户比例较高，建议产品设计考虑易用性和功能实用性。</p>"""

                # 性别分析
                if gender_data and len(gender_data) > 1:
                    male_rate = 0
                    female_rate = 0
                    for name, rate in gender_data:
                        if "男" in name:
                            male_rate = rate
                        elif "女" in name:
                            female_rate = rate

                    dominant_gender = "男性" if male_rate > female_rate else "女性"
                    ratio = max(male_rate, female_rate) / min(male_rate, female_rate) if min(male_rate,
                                                                                             female_rate) > 0 else 0

                    html_content += f"""
                    <p><strong>性别分布:</strong> 搜索该关键词的用户中，<span class="highlight">{dominant_gender}</span>占主导，
                    男女比例约为{male_rate:.1f}:{female_rate:.1f}。"""

                    if ratio > 2:
                        html_content += f"性别差异<span class=\"highlight\">显著</span>，建议重点关注{dominant_gender}用户需求。"
                    else:
                        html_content += "男女分布较为平衡，建议兼顾不同性别用户需求。"

                    html_content += "</p>"

                # 地域分布
                if region_data:
                    top_regions = region_data[:3]
                    region_names = [name for name, _ in top_regions]

                    html_content += f"""
                    <p><strong>地域分布:</strong> 搜索热度主要集中在<span class="highlight">{'、'.join(region_names)}</span>等地区。
                    """

                    # 判断是否集中在一线城市
                    first_tier = ["北京", "上海", "广州", "深圳"]
                    if any(city in name for name, _ in top_regions for city in first_tier):
                        html_content += "一线城市用户关注度较高，表明产品/服务在发达地区有较大市场。"
                    elif all(("省" in name or "自治区" in name) for name, _ in top_regions):
                        html_content += "主要分布在省级行政区，表明产品/服务在全国范围内有广泛需求。"

                    html_content += "</p>"

                html_content += """
                </div>
                """

            # 需求分析 - 文字总结
            if include_predictions and demand_data:
                html_content += """
                <div class="section">
                    <h2>需求分析</h2>
                """

                if demand_data:
                    top_demands = demand_data[:5]
                    html_content += f"""
                    <p><strong>热门搜索词:</strong> 与"{keyword}"相关的热门搜索包括
                    <span class="highlight">{'、'.join([word for word, _ in top_demands])}</span>。</p>

                    <p>这表明用户在搜索{keyword}时，主要关注以下几个方面：</p>
                    <ul>
                    """

                    # 分析搜索词特点
                    has_price = any("价格" in word or "多少钱" in word for word, _ in top_demands)
                    has_brand = any("品牌" in word or "排行" in word for word, _ in top_demands)
                    has_function = any("怎么" in word or "如何" in word or "功能" in word for word, _ in top_demands)

                    if has_price:
                        html_content += "<li>产品或服务的<span class=\"highlight\">价格因素</span>，表明价格是用户决策的重要考量</li>"
                    if has_brand:
                        html_content += "<li>关注<span class=\"highlight\">品牌和排名</span>，表明用户在寻找可靠和有口碑的选择</li>"
                    if has_function:
                        html_content += "<li>产品的<span class=\"highlight\">功能和使用方法</span>，表明用户关注实用性和易用性</li>"

                    html_content += f"""
                    <li>搜索词中的高频内容反映了用户对{keyword}的主要需求和关注点</li>
                    </ul>
                    """

                html_content += """
                </div>
                """

            # 分析建议部分保持不变，因为已经是总结性的
            if include_recommendations:
                # 分析建议基于实际数据
                recommendations = []

                # 基于热门地区的建议
                if region_data:
                    top_regions = [region for region, _ in region_data[:3]]
                    recommendations.append(f"在{'、'.join(top_regions)}等热门地区增加营销投入")

                # 基于人群特征的建议
                if age_data:
                    max_age = max(age_data, key=lambda x: x[1])
                    recommendations.append(f"针对{max_age[0]}年龄段用户优化产品设计和营销内容")

                # 基于兴趣特征的建议
                if interest_data:
                    top_interests = [interest for interest, _ in interest_data[:2]]
                    recommendations.append(f"结合用户对{'和'.join(top_interests)}的兴趣，开发相关功能或内容")

                # 基于需求词的建议
                if demand_data:
                    top_demands = [word for word, _ in demand_data[:2]]
                    recommendations.append(f"针对用户关注的{'和'.join(top_demands)}等热门话题，提供专业内容")

                # 基于趋势的建议
                if trend_data and len(trend_data) > 1:
                    values = [val for _, val in trend_data if val is not None]
                    if values:
                        start_value = values[0]
                        end_value = values[-1]
                        change_percent = ((end_value - start_value) / start_value * 100) if start_value > 0 else 0

                        if change_percent > 20:
                            recommendations.append("把握搜索热度上升趋势，加大市场投入力度")
                        elif change_percent < -20:
                            recommendations.append("关注搜索热度下降趋势，寻找新的增长点")

                # 通用建议
                recommendations.append("持续跟踪市场趋势，及时调整产品策略")

                # 如果没有足够的建议，添加一些通用的
                if len(recommendations) < 3:
                    recommendations.append("建立完整的用户转化渠道，提高获客效率")
                    recommendations.append("优化搜索引擎营销策略，提升曝光和点击率")

                html_content += """
                <div class="section">
                    <h2>分析建议</h2>
                    <div class="recommendation">
                        <ol>
                """

                for recommendation in recommendations[:5]:  # 最多显示5条建议
                    html_content += f"""
                            <li>{recommendation}</li>
                    """

                html_content += """
                        </ol>
                    </div>
                </div>
                """

            # 结束HTML文档
            html_content += """
            </body>
            </html>"""

            # 保存HTML文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(html_content)

            logging.info(f"HTML报告已成功生成: {file_path}")
            return True

        except Exception as e:
            logging.error(f"创建HTML报告失败: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def create_cluster_analysis_page(self):
        """创建聚类分析页面"""
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # 创建标题
        title_label = QLabel("聚类分析")
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

        # 创建标签页
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
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

        # 添加热门关键词分析标签页
        tab_widget.addTab(self.create_hot_keywords_tab(), "热门关键词分析")
        tab_widget.addTab(self.create_keyword_data_tab(), "关键词数据获取")
        tab_widget.addTab(self.create_cluster_result_tab(), "聚类结果展示")

        layout.addWidget(tab_widget)
        page.setLayout(layout)
        return page

    def create_hot_keywords_tab(self):
        """创建热门关键词分析标签页"""
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # 创建控制面板
        control_layout = QHBoxLayout()

        # 添加关键词输入框
        keyword_label = QLabel("关键词:")
        keyword_label.setStyleSheet("color: white;")
        self.hot_keyword_input = QLineEdit()
        self.hot_keyword_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                background: rgba(255, 255, 255, 0.2);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 5px;
                color: white;
                min-width: 200px;
            }
        """)

        # 添加获取按钮
        self.get_hot_keywords_btn = QPushButton("获取热门关键词")
        self.get_hot_keywords_btn.setStyleSheet("""
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
        self.get_hot_keywords_btn.clicked.connect(self.get_hot_keywords)

        control_layout.addWidget(keyword_label)
        control_layout.addWidget(self.hot_keyword_input)
        control_layout.addWidget(self.get_hot_keywords_btn)
        control_layout.addStretch()
        layout.addLayout(control_layout)

        # 创建词云显示区域
        self.wordcloud_widget = QWidget()
        self.wordcloud_widget.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
            }
        """)
        layout.addWidget(self.wordcloud_widget)

        tab.setLayout(layout)
        return tab

    def get_hot_keywords(self):
        """从数据库获取热门关键词并生成词云"""
        try:
            keyword = self.hot_keyword_input.text().strip()
            if not keyword:
                self.show_message("错误", "请输入关键词")
                return

            # 从数据库获取数据
            db = DatabaseConnection()
            try:
                # 查询前10个PV值最高的关键词
                query = """
                    SELECT word, pv 
                    FROM human_request_data 
                    WHERE word LIKE %s 
                    ORDER BY pv DESC 
                    LIMIT 10
                """
                db.cursor.execute(query, (f"%{keyword}%",))
                results = db.cursor.fetchall()

                if not results:
                    self.show_message("提示", "未找到相关热门关键词")
                    return

                # 构建关键词字典
                hot_keywords = {row[0]: float(row[1]) for row in results}

                # 保存关键词数据到类属性
                self.wordcloud_keywords = hot_keywords

                # 启动多线程数据获取
                username, _ = get_login_user_info()
                if not username:
                    self.show_message("错误", "获取用户信息失败")
                    return

                # 创建并启动线程
                threads = []
                for i, word in enumerate(hot_keywords.keys()):
                    thread = KeywordDataCollectionThread(word, username, i + 1)
                    threads.append(thread)
                    thread.start()

                # 等待所有线程完成
                for thread in threads:
                    thread.join()

                # 检查结果
                failed_keywords = [t.keyword for t in threads if not t.result]
                if failed_keywords:
                    self.show_message("警告", f"以下关键词数据获取失败：\n{', '.join(failed_keywords)}")

                # 生成词云
                self.generate_wordcloud(hot_keywords)

                # 显示成功消息
                self.show_message("成功", "热门关键词获取成功")

            finally:
                db.close()

        except Exception as e:
            logging.error(f"获取热门关键词失败: {str(e)}")
            self.show_message("错误", f"获取热门关键词失败: {str(e)}")

    def generate_wordcloud(self, keywords):
        """生成词云图"""
        if not keywords:
            self.show_message("错误", "没有关键词数据可供显示")
            return

        try:
            # 创建Figure和Canvas
            fig = Figure(figsize=(10, 6), facecolor='white')
            canvas = FigureCanvas(fig)

            # 清除之前的布局
            if self.wordcloud_widget.layout():
                for i in reversed(range(self.wordcloud_widget.layout().count())):
                    item = self.wordcloud_widget.layout().itemAt(i)
                    if item.widget():
                        item.widget().setParent(None)
            else:
                self.wordcloud_widget.setLayout(QVBoxLayout())

            # 设置新的布局
            layout = self.wordcloud_widget.layout()
            layout.addWidget(canvas)

            # 生成词云
            ax = fig.add_subplot(111)
            ax.axis('off')
            fig.patch.set_alpha(1.0)
            ax.patch.set_alpha(1.0)

            # 创建词云对象
            wordcloud = WordCloud(
                width=1200,
                height=800,
                background_color='white',
                font_path='C:/Windows/Fonts/msyh.ttc',  # 使用微软雅黑字体
                max_words=100,
                max_font_size=120,
                min_font_size=10,
                random_state=42,
                prefer_horizontal=0.7,
                scale=2,
                colormap='viridis',
                relative_scaling=0.5,
                margin=10
            )

            # 生成词云
            wordcloud.generate_from_frequencies(keywords)

            # 显示词云
            ax.imshow(wordcloud, interpolation='bilinear')
            canvas.draw()

        except Exception as e:
            logging.error(f"生成词云失败: {str(e)}")
            self.show_message("错误", f"生成词云失败: {str(e)}")

    def create_keyword_data_tab(self):
        """创建关键词数据提取标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 创建数据表格
        self.keyword_data_table = QTableWidget()
        self.keyword_data_table.setColumnCount(5)
        self.keyword_data_table.setHorizontalHeaderLabels(['关键词', '搜索指数', '人群画像', '需求分布', '地域分布'])
        self.keyword_data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # 创建按钮
        button_layout = QHBoxLayout()
        fetch_button = QPushButton('提取数据')
        fetch_button.clicked.connect(self.fetch_keyword_data)
        analyze_button = QPushButton('开始聚类分析')
        analyze_button.clicked.connect(self.perform_cluster_analysis)
        button_layout.addWidget(fetch_button)
        button_layout.addWidget(analyze_button)

        # 创建进度条
        self.keyword_progress = QProgressBar()
        self.keyword_progress.hide()

        # 添加到布局
        layout.addWidget(QLabel('热门关键词数据'))
        layout.addWidget(self.keyword_data_table)
        layout.addLayout(button_layout)
        layout.addWidget(self.keyword_progress)

        return tab

    def fetch_keyword_data(self):
        """从数据库提取关键词数据"""
        try:
            # 获取词云中的关键词
            if not hasattr(self, 'wordcloud_keywords') or not self.wordcloud_keywords:
                QMessageBox.warning(self, "错误", "请先在第一页获取热门关键词")
                return

            # 显示进度条
            self.keyword_progress.show()
            self.keyword_progress.setValue(0)

            # 清空表格
            self.keyword_data_table.setRowCount(0)

            # 获取当前登录用户信息
            username, _ = get_login_user_info()
            if not username:
                QMessageBox.warning(self, "错误", "未获取到用户信息，请重新登录")
                return

            # 计算进度步长
            keywords = list(self.wordcloud_keywords.keys())
            progress_step = 100 / len(keywords)
            current_progress = 0

            # 创建数据库连接
            db = DatabaseConnection()

            try:
                for keyword in keywords:
                    # 获取趋势数据
                    trend_data = db.get_trend_data(keyword)
                    avg_index = sum(float(d.get('index', 0)) for d in trend_data) / len(trend_data) if trend_data else 0

                    # 获取其他数据
                    portrait_data = db.get_portrait_data(keyword)
                    demand_data = db.get_demand_data(keyword)
                    region_data = db.get_region_data(keyword)

                    # 添加到表格
                    row = self.keyword_data_table.rowCount()
                    self.keyword_data_table.insertRow(row)
                    self.keyword_data_table.setItem(row, 0, QTableWidgetItem(keyword))
                    self.keyword_data_table.setItem(row, 1, QTableWidgetItem(f"{avg_index:.2f}"))
                    self.keyword_data_table.setItem(row, 2, QTableWidgetItem("已获取" if portrait_data else "未获取"))
                    self.keyword_data_table.setItem(row, 3, QTableWidgetItem("已获取" if demand_data else "未获取"))
                    self.keyword_data_table.setItem(row, 4, QTableWidgetItem("已获取" if region_data else "未获取"))

                    # 更新进度
                    current_progress += progress_step
                    self.keyword_progress.setValue(int(current_progress))

                self.keyword_progress.setValue(100)
                QMessageBox.information(self, "成功", "数据提取完成")

            finally:
                db.close()

        except Exception as e:
            QMessageBox.warning(self, "错误", f"数据提取失败: {str(e)}")
            logging.error(f"数据提取失败: {str(e)}")
        finally:
            self.keyword_progress.hide()

    def perform_cluster_analysis(self):
        """执行聚类分析"""
        try:
            # 检查是否有数据
            if self.keyword_data_table.rowCount() == 0:
                QMessageBox.warning(self, "错误", "请先提取关键词数据")
                return

            # 收集数据
            data = []
            for row in range(self.keyword_data_table.rowCount()):
                keyword = self.keyword_data_table.item(row, 0).text()
                index = float(self.keyword_data_table.item(row, 1).text())
                data.append([keyword, index])

            # 准备数据进行聚类
            from sklearn.cluster import KMeans
            import numpy as np

            # 提取搜索指数数据进行聚类
            X = np.array([d[1] for d in data]).reshape(-1, 1)

            # 使用K-means聚类
            kmeans = KMeans(n_clusters=3, random_state=42)
            clusters = kmeans.fit_predict(X)

            # 保存聚类结果
            self.cluster_results = {
                'keywords': [d[0] for d in data],
                'values': [d[1] for d in data],
                'clusters': clusters.tolist(),
                'cluster_centers': kmeans.cluster_centers_.flatten().tolist()
            }

            # 更新第三个标签页
            self.update_cluster_results_tab()

            QMessageBox.information(self, "成功", "聚类分析完成，请切换到第三个标签页查看结果")

        except Exception as e:
            QMessageBox.warning(self, "错误", f"聚类分析失败: {str(e)}")
            logging.error(f"聚类分析失败: {str(e)}")

    def create_cluster_result_tab(self):
        """创建聚类结果展示标签页"""
        tab = QWidget()
        layout = QVBoxLayout(tab)

        # 创建结果展示区域
        self.cluster_result_text = QTextEdit()
        self.cluster_result_text.setReadOnly(True)

        # 创建图表展示区域
        self.cluster_plot_widget = QWidget()
        self.cluster_plot_layout = QVBoxLayout(self.cluster_plot_widget)

        # 添加到主布局
        layout.addWidget(QLabel('聚类分析结果'))
        layout.addWidget(self.cluster_result_text)
        layout.addWidget(self.cluster_plot_widget)

        return tab

    def update_cluster_results_tab(self):
        """更新聚类结果展示"""
        if not hasattr(self, 'cluster_results'):
            return

        # 清空现有内容
        self.cluster_result_text.clear()
        for i in reversed(range(self.cluster_plot_layout.count())):
            self.cluster_plot_layout.itemAt(i).widget().setParent(None)

        # 生成结果报告
        report = self.generate_cluster_report()
        self.cluster_result_text.setHtml(report)

        # 创建聚类可视化
        self.create_cluster_visualization()

    def generate_cluster_report(self):
        """生成聚类分析报告"""
        if not hasattr(self, 'cluster_results'):
            return ""

        # 获取聚类结果
        keywords = self.cluster_results['keywords']
        values = self.cluster_results['values']
        clusters = self.cluster_results['clusters']
        centers = self.cluster_results['cluster_centers']

        # 将关键词按聚类分组
        cluster_groups = {i: [] for i in range(3)}
        for keyword, value, cluster in zip(keywords, values, clusters):
            cluster_groups[cluster].append((keyword, value))

        # 生成HTML报告
        html = "<h3>聚类分析结果摘要</h3>"
        html += "<p>基于搜索指数对关键词进行聚类分析，共分为3个类别：</p>"

        # 对聚类中心值进行排序，确定高中低分类
        center_indices = sorted(range(3), key=lambda i: centers[i], reverse=True)
        categories = ["高热度关键词", "中等热度关键词", "低热度关键词"]
        descriptions = [
            "这些关键词具有最高的搜索指数，表明它们是最受关注的话题。",
            "这些关键词具有中等水平的搜索指数，代表稳定的关注度。",
            "这些关键词的搜索指数相对较低，可能是新兴或小众话题。"
        ]

        for i, cluster_id in enumerate(center_indices):
            keywords_in_cluster = cluster_groups[cluster_id]
            avg_value = centers[cluster_id]

            html += f"<h4>类别 {i + 1}: {categories[i]}</h4>"
            html += f"<p>{descriptions[i]}</p>"
            html += f"<p>中心值：{avg_value:.2f}</p>"
            html += "<p>包含的关键词：</p><ul>"

            # 按搜索指数降序排序关键词
            sorted_keywords = sorted(keywords_in_cluster, key=lambda x: x[1], reverse=True)
            for keyword, value in sorted_keywords:
                html += f"<li>{keyword} (搜索指数: {value:.2f})</li>"

            html += "</ul>"

        return html

    def create_cluster_visualization(self):
        """创建聚类结果可视化"""
        if not hasattr(self, 'cluster_results'):
            return

        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
        import numpy as np

        # 创建图表
        fig, ax = plt.subplots(figsize=(10, 6))

        # 获取数据
        values = np.array(self.cluster_results['values'])
        clusters = np.array(self.cluster_results['clusters'])
        keywords = self.cluster_results['keywords']
        centers = np.array(self.cluster_results['cluster_centers'])

        # 设置颜色方案
        colors = ['#FF9999', '#66B2FF', '#99FF99']
        cluster_names = ['高热度', '中等热度', '低热度']

        # 创建散点图
        for i in range(3):
            mask = clusters == i
            scatter = ax.scatter(np.arange(len(values))[mask],
                                 values[mask],
                                 c=colors[i],
                                 label=cluster_names[i],
                                 alpha=0.6,
                                 s=100)

        # 添加聚类中心线
        for i, center in enumerate(centers):
            ax.axhline(y=center, color=colors[i], linestyle='--', alpha=0.3)

        # 添加关键词标签
        for i, (keyword, value) in enumerate(zip(keywords, values)):
            ax.annotate(keyword,
                        (i, value),
                        textcoords="offset points",
                        xytext=(0, 10),
                        ha='center',
                        fontsize=8)

        # 设置图表样式
        ax.set_title('关键词聚类分布图', fontsize=12, pad=20)
        ax.set_xlabel('关键词序号', fontsize=10)
        ax.set_ylabel('搜索指数', fontsize=10)
        ax.legend(title='聚类类别')
        ax.grid(True, linestyle='--', alpha=0.3)

        # 调整布局
        plt.tight_layout()

        # 创建画布并添加到界面
        canvas = FigureCanvas(fig)
        self.cluster_plot_layout.addWidget(canvas)

    def create_about_page(self):
        """创建关于页面"""
        page = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)

        # 创建标题
        title_label = QLabel("关于系统")
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

        # 创建版本信息
        version_label = QLabel("版本: 2.0.0")
        version_label.setFont(QFont("Microsoft YaHei", 14))
        version_label.setStyleSheet("color: white;")
        version_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(version_label)

        # 创建系统信息
        info_text = """
        <p style='color: white; font-size: 14px; line-height: 1.5;'>
        养老需求分析系统是一个功能强大的数据采集与分析平台，支持多地区、多关键词的数据采集，
        提供数据可视化、数据预测和人群画像分析，同时具备完善的用户管理系统。
        </p>
        <p style='color: white; font-size: 14px; line-height: 1.5;'>
        主要功能：
        • 支持全国、区域、省份、城市级别的数据采集
        • 自动登录百度指数平台
        • 支持多关键词数据采集
        • 数据自动保存到Excel和本地数据库
        • 人群画像分析功能
        • 数据预测与趋势分析
        • 数据可视化展示
        </p>
        """
        info_label = QLabel(info_text)
        info_label.setWordWrap(True)
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)

        # 添加版权信息
        copyright_label = QLabel("© 2025 养老需求分析系统 版权所有")
        copyright_label.setFont(QFont("Microsoft YaHei", 12))
        copyright_label.setStyleSheet("color: rgba(255, 255, 255, 0.7);")
        copyright_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(copyright_label)

        layout.addStretch()
        page.setLayout(layout)
        return page

    def switch_page(self, index):
        item = self.function_list.item(index)
        if not item:
            return
        item_text = item.data(Qt.UserRole) or item.text().split('\n')[0]
        if item_text == "用户管理":
            self.user_management_window = UserManagementWindow(self)
            self.user_management_window.show()
            return
        # 其他功能切换逻辑...