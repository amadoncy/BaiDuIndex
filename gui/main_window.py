from PyQt5.QtWidgets import (QMainWindow, QWidget, QLabel,
                             QVBoxLayout, QHBoxLayout, QPushButton,
                             QMessageBox, QListWidget, QStackedWidget,
                             QListWidgetItem, QFrame, QComboBox, QSpinBox,
                             QLineEdit, QProgressBar, QTextEdit, QTabWidget,
                             QTableWidget, QTableWidgetItem, QHeaderView,
                             QGroupBox)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QSize, QThread, pyqtSignal, QUrl
from PyQt5.QtGui import QFont, QColor, QPalette, QLinearGradient, QPainter, QIcon
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineSettings
import os
import logging
import datetime
from utils.get_local_weather_utils import get_weather_info
import requests
import json
from utils.get_trend_utils import get_trend_utils, select_area
from config.city_codes import get_all_regions, get_region_provinces, get_province_cities
from pyecharts import options as opts
from pyecharts.charts import Line, Bar, Pie, Map, Graph, Page
from utils import db_utils
from gui.data_display_window import DataDisplayWindow

class DataCollectionThread(QThread):
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
        # Get the base directory path
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
                    # 调用需求图谱数据采集函数
                    from utils.get_huamn_requestion_utils import get_human_request_data
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
                {"title": "导出数据", "description": "导出数据到Excel"},
                {"title": "系统设置", "description": "调整系统配置"}
            ]

            for function in functions:
                item = QListWidgetItem(f"{function['title']}\n{function['description']}")
                item.setData(Qt.UserRole, function['title'])  # 存储功能名称
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
            self.content_stack.addWidget(self.create_export_page())
            self.content_stack.addWidget(self.create_settings_page())

            # 连接功能列表的选择信号
            self.function_list.currentRowChanged.connect(self.content_stack.setCurrentIndex)

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
            if self.collection_thread and self.collection_thread.isRunning():
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
        return DataDisplayWindow()

    def create_export_page(self):
        """创建导出数据页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel("导出数据功能开发中...")
        label.setFont(QFont("Microsoft YaHei", 16))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        return page

    def create_settings_page(self):
        """创建系统设置页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setSpacing(20)

        # 添加设置页面标题
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

        # 创建设置选项容器
        settings_container = QFrame()
        settings_container.setStyleSheet("""
            QFrame {
                background: rgba(255, 255, 255, 0.1);
                border-radius: 15px;
                padding: 20px;
            }
            QLabel {
                color: white;
                font-size: 14px;
            }
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                border: 2px solid white;
                border-radius: 8px;
                color: white;
                padding: 8px 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
            }
            QComboBox {
                background-color: rgba(255, 255, 255, 0.2);
                border: 2px solid white;
                border-radius: 8px;
                color: white;
                padding: 8px;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(resources/down_arrow.png);
                width: 12px;
                height: 12px;
            }
            QSpinBox {
                background-color: rgba(255, 255, 255, 0.2);
                border: 2px solid white;
                border-radius: 8px;
                color: white;
                padding: 8px;
                min-width: 80px;
            }
        """)

        settings_layout = QVBoxLayout(settings_container)
        settings_layout.setSpacing(15)

        # 1. 天气更新频率设置
        weather_group = QHBoxLayout()
        weather_label = QLabel("天气更新频率：")
        weather_combo = QComboBox()
        weather_combo.setObjectName('weather_combo')  # 设置对象名称
        weather_combo.addItems(["10分钟", "30分钟", "1小时", "2小时"])
        weather_combo.setCurrentText("30分钟")
        weather_combo.currentTextChanged.connect(self.update_weather_interval)
        weather_group.addWidget(weather_label)
        weather_group.addWidget(weather_combo)
        weather_group.addStretch()
        settings_layout.addLayout(weather_group)

        # 2. 字体大小设置
        font_group = QHBoxLayout()
        font_label = QLabel("界面字体大小：")
        font_size_spin = QSpinBox()
        font_size_spin.setObjectName('font_size_spin')  # 设置对象名称
        font_size_spin.setRange(12, 20)
        font_size_spin.setValue(14)
        font_size_spin.valueChanged.connect(self.update_font_size)
        font_group.addWidget(font_label)
        font_group.addWidget(font_size_spin)
        font_group.addStretch()
        settings_layout.addLayout(font_group)

        # 3. 主题设置
        theme_group = QHBoxLayout()
        theme_label = QLabel("界面主题：")
        theme_combo = QComboBox()
        theme_combo.setObjectName('theme_combo')  # 设置对象名称
        theme_combo.addItems(["深蓝主题", "暗夜主题", "浅色主题"])
        theme_combo.currentTextChanged.connect(self.update_theme)
        theme_group.addWidget(theme_label)
        theme_group.addWidget(theme_combo)
        theme_group.addStretch()
        settings_layout.addLayout(theme_group)

        # 4. 数据缓存设置
        cache_group = QHBoxLayout()
        cache_label = QLabel("数据缓存：")
        clear_cache_btn = QPushButton("清除缓存")
        clear_cache_btn.clicked.connect(self.clear_cache)
        cache_group.addWidget(cache_label)
        cache_group.addWidget(clear_cache_btn)
        cache_group.addStretch()
        settings_layout.addLayout(cache_group)

        # 5. 关于系统
        about_group = QHBoxLayout()
        about_label = QLabel("关于系统：")
        about_btn = QPushButton("查看详情")
        about_btn.clicked.connect(self.show_about)
        about_group.addWidget(about_label)
        about_group.addWidget(about_btn)
        about_group.addStretch()
        settings_layout.addLayout(about_group)

        # 添加设置容器到主布局
        layout.addWidget(settings_container)
        layout.addStretch()

        # 加载保存的设置
        self.load_settings()

        return page

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
            logging.error(f"更新天气更新频率失败: {str(e)}")
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
            settings = {
                'theme': self.findChild(QComboBox, 'theme_combo').currentText(),
                'font_size': self.findChild(QSpinBox, 'font_size_spin').value(),
                'weather_interval': self.findChild(QComboBox, 'weather_combo').currentText()
            }

            settings_path = os.path.join(self.cache_dir, 'settings.json')
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
        except Exception as e:
            logging.error(f"保存设置失败: {str(e)}")

    def load_settings(self):
        """加载保存的设置"""
        try:
            settings_path = os.path.join(self.cache_dir, 'settings.json')
            if os.path.exists(settings_path):
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
        except Exception as e:
            logging.error(f"加载设置失败: {str(e)}")

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
        
        # 先添加空标签页到标签页控件
        self.analysis_tabs.addTab(self.portrait_tab, "人群画像分析")
        self.analysis_tabs.addTab(self.demand_tab, "需求图谱分析")
        
        # 初始化标签页的内容
        self.init_portrait_tab()
        self.init_demand_tab()

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
            if isinstance(selected_date, datetime.date):
                selected_date = selected_date.strftime('%Y-%m-%d')
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

            # 处理数据 - 采样优化
            total_points = len(results)
            sample_size = min(total_points, 100)  # 最多显示100个数据点
            step = max(1, total_points // sample_size)

            dates = []
            values = []
            for i in range(0, total_points, step):
                row = results[i]
                if isinstance(row[0], datetime.date):
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

            # 优化全局配置
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
                        range_start=0,
                        range_end=100,
                        pos_bottom="5%"
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
            # 将字符串日期转换为datetime.date对象
            if isinstance(date, str):
                date = datetime.datetime.strptime(date, '%Y-%m-%d').date()

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
                    <td>{i+1}</td>
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