from PyQt5.QtWidgets import (QMainWindow, QWidget, QLabel, 
                             QVBoxLayout, QHBoxLayout, QPushButton,
                             QMessageBox, QListWidget, QStackedWidget,
                             QListWidgetItem, QFrame, QComboBox, QSpinBox,
                             QLineEdit, QProgressBar, QTextEdit)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QSize, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette, QLinearGradient, QPainter, QIcon
import os
import logging
from utils.get_local_weather_utils import get_weather_info
import requests
import json
import pandas as pd
from datetime import datetime, timedelta, date
from utils.get_trend_utils import get_trend_utils, select_area
from config.city_codes import get_all_regions, get_region_provinces, get_province_cities
from utils.get_index_cookie_utils import get_index_cookie, get_login_user_info
from utils.get_huamn_requestion_utils import get_human_request_data

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
                    self.finished_signal.emit(True, "数据采集完成")
                else:
                    self.finished_signal.emit(False, "数据采集失败")
            elif self.collection_type == "portrait":
                # 人群画像数据采集
                self.progress_signal.emit("正在采集人群画像数据...")
                # TODO: 实现人群画像数据采集
                if self._is_running:
                    self.finished_signal.emit(True, "人群画像数据采集完成")
            elif self.collection_type == "demand":
                # 需求图谱数据采集
                self.progress_signal.emit("正在采集需求图谱数据...")
                try:
                    # 获取当前日期作为结束日期
                    end_date = date.today()
                    # 设置开始日期为7天前
                    start_date = end_date - timedelta(days=7)
                    
                    # 调用需求图谱数据采集函数
                    success = get_human_request_data(self.keyword, start_date, end_date, self.username)
                    
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
                    self.weather_label.setText(f"{city_name}\n当前温度: {weather_info['temp']}°C\n天气：{weather_info['text']}")
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
            else:
                QMessageBox.warning(self, "错误", message)

            # 清理线程
            if self.collection_thread:
                self.collection_thread.stop()
                self.collection_thread.wait()
                self.collection_thread = None

        except Exception as e:
            logging.error(f"处理采集完成事件时发生错误: {str(e)}")
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
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel("数据展示功能开发中...")
        label.setFont(QFont("Microsoft YaHei", 16))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        return page
        
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
        self.function_list.setStyleSheet(self.function_list.styleSheet() + "\nbackground-color: rgba(255, 255, 255, 0);")
        
        animation = QPropertyAnimation(self.function_list, b"pos")
        animation.setDuration(1000)
        animation.setStartValue(QPoint(self.function_list.x() - 50, self.function_list.y()))
        animation.setEndValue(QPoint(self.function_list.x(), self.function_list.y()))
        animation.setEasingCurve(QEasingCurve.OutBack)
        animation.start()
        
        # 为内容区域添加淡入动画
        self.content_stack.setStyleSheet(self.content_stack.styleSheet() + "\nbackground-color: rgba(255, 255, 255, 0);")
        
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
            if self.collection_thread and self.collection_thread.isRunning():
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

        # 添加分析功能说明
        info_label = QLabel("""
        数据分析功能包括：
        1. 趋势分析：分析关键词搜索量的变化趋势
        2. 地域分布：分析不同地区的搜索热度差异
        3. 相关性分析：分析不同关键词之间的相关性
        4. 预测分析：基于历史数据预测未来趋势
        """)
        info_label.setStyleSheet("""
            QLabel {
                color: white;
                background: rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 20px;
                font-size: 14px;
                line-height: 1.5;
            }
        """)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        # 添加开发中提示
        dev_label = QLabel("此功能正在开发中，敬请期待...")
        dev_label.setStyleSheet("color: white; font-size: 16px;")
        dev_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(dev_label)

        layout.addStretch()
        return page 