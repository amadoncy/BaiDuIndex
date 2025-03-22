from PyQt5.QtWidgets import (QMainWindow, QWidget, QLabel, 
                             QVBoxLayout, QHBoxLayout, QPushButton,
                             QMessageBox, QListWidget, QStackedWidget,
                             QListWidgetItem, QFrame, QComboBox, QSpinBox)
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, QPoint, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QLinearGradient, QPainter, QIcon
import os
import logging
from utils.get_local_weather_utils import get_weather_info
import requests
import json

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
        label = QLabel("数据采集功能开发中...")
        label.setFont(QFont("Microsoft YaHei", 16))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        return page
        
    def create_data_analysis_page(self):
        """创建数据分析页面"""
        page = QWidget()
        layout = QVBoxLayout(page)
        label = QLabel("数据分析功能开发中...")
        label.setFont(QFont("Microsoft YaHei", 16))
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        return page
        
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
            # 停止天气更新定时器
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