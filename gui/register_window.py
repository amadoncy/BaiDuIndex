from PyQt5.QtWidgets import (QWidget, QLineEdit, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QLabel,
                             QMainWindow, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QBrush, QImage, QIcon
import os
import logging
from utils.db_utils import DatabaseConnection
from utils.captcha_utils import CaptchaManager
from utils.validation_utils import ValidationUtils

class RegisterWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()
        self.parent_window = parent
        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'logo.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.ui = Ui_RegisterWindow()
        self.ui.setupUi(self)
        self.db = DatabaseConnection()
        self.captcha_manager = CaptchaManager()
        self.validation = ValidationUtils()
        self.current_captcha_id = None
        
        # 绑定按钮事件
        self.ui.register_btn.clicked.connect(self.handle_register)
        self.ui.back_btn.clicked.connect(self.back_to_login)
        self.ui.refresh_captcha_btn.clicked.connect(self.refresh_captcha)
        
        # 绑定密码输入事件
        self.ui.password.textChanged.connect(self.check_password_strength)
        
        # 生成初始验证码
        self.refresh_captcha()

    def check_password_strength(self):
        """检查密码强度"""
        password = self.ui.password.text()
        level, tips = self.validation.check_password_strength(password)
        
        # 设置提示文字颜色
        color = "#dc3545" if level == 0 else "#ffc107" if level == 1 else "#28a745"
        style = f"color: {color};"
        
        self.ui.password_tips.setStyleSheet(style)
        self.ui.password_tips.setText(tips)

    def refresh_captcha(self):
        """刷新验证码"""
        try:
            captcha_id, captcha_image = self.captcha_manager.generate_captcha()
            if captcha_id and captcha_image:
                self.current_captcha_id = captcha_id
                self.ui.captcha_label.setPixmap(captcha_image)
        except Exception as e:
            logging.error(f"刷新验证码失败: {str(e)}")
            QMessageBox.warning(self, "错误", "刷新验证码失败，请检查Redis服务是否启动")

    def handle_register(self):
        """处理注册逻辑"""
        try:
            logging.debug("开始处理注册请求...")
            username = self.ui.username.text().strip()
            password = self.ui.password.text().strip()
            confirm_password = self.ui.confirm_password.text().strip()
            phone = self.ui.phone.text().strip()
            email = self.ui.email.text().strip()
            captcha = self.ui.yanzhengma.text().strip()
            
            logging.debug(f"注册信息 - 用户名: {username}, 手机号: {phone}, 邮箱: {email}")
            
            # 输入验证
            if not username or not password or not confirm_password or not phone or not email:
                logging.warning("必填项未填写完整")
                QMessageBox.warning(self, "警告", "请填写所有必填项！")
                return
                
            if not captcha:
                logging.warning("验证码为空")
                QMessageBox.warning(self, "警告", "请输入验证码！")
                return
                
            if password != confirm_password:
                logging.warning("两次输入的密码不一致")
                QMessageBox.warning(self, "警告", "两次输入的密码不一致！")
                return
                
            if len(password) < 6:
                logging.warning("密码长度不足6位")
                QMessageBox.warning(self, "警告", "密码长度不能少于6位！")
                return
                
            if not self.validation.validate_phone(phone):
                logging.warning("手机号格式不正确")
                QMessageBox.warning(self, "警告", "手机号格式不正确！")
                return
                
            if not self.validation.validate_email(email):
                logging.warning("邮箱格式不正确")
                QMessageBox.warning(self, "警告", "邮箱格式不正确！")
                return
                
            # 验证验证码
            logging.debug("开始验证验证码...")
            if not self.current_captcha_id:
                logging.error("验证码ID不存在")
                QMessageBox.warning(self, "错误", "验证码已过期，请刷新验证码！")
                self.refresh_captcha()
                return
                
            if not self.captcha_manager.verify_captcha(self.current_captcha_id, captcha):
                logging.warning("验证码验证失败")
                QMessageBox.warning(self, "错误", "验证码错误或已过期！")
                self.refresh_captcha()
                self.ui.yanzhengma.clear()
                return
                
            logging.debug("验证码验证成功")
                
            # 注册用户
            logging.debug("开始连接数据库...")
            if not self.db.connect():
                logging.error("数据库连接失败")
                QMessageBox.warning(self, "错误", "数据库连接失败，请稍后重试！")
                return
                
            logging.debug("数据库连接成功")
            
            # 检查用户名是否已存在
            check_query = "SELECT id FROM users WHERE username = %s OR phone = %s OR email = %s"
            logging.debug(f"检查用户信息是否已存在 - username: {username}, phone: {phone}, email: {email}")
            self.db.cursor.execute(check_query, (username, phone, email))
            result = self.db.cursor.fetchone()
            
            if result:
                # 进一步检查具体是哪个字段重复
                self.db.cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                if self.db.cursor.fetchone():
                    logging.warning("用户名已被注册")
                    QMessageBox.warning(self, "错误", "该用户名已被注册！")
                    return
                    
                self.db.cursor.execute("SELECT id FROM users WHERE phone = %s", (phone,))
                if self.db.cursor.fetchone():
                    logging.warning("手机号已被注册")
                    QMessageBox.warning(self, "错误", "该手机号已被注册！")
                    return
                    
                self.db.cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                if self.db.cursor.fetchone():
                    logging.warning("邮箱已被注册")
                    QMessageBox.warning(self, "错误", "该邮箱已被注册！")
                    return
                
            # 插入新用户
            insert_query = "INSERT INTO users (username, password, phone, email) VALUES (%s, %s, %s, %s)"
            logging.debug("开始插入新用户数据...")
            self.db.cursor.execute(insert_query, (username, password, phone, email))
            logging.debug("执行commit操作...")
            self.db.connection.commit()
            logging.debug("数据提交成功")
            
            # 显示成功消息
            QMessageBox.information(self, "成功", "注册成功！\n请返回登录界面进行登录。")
            
            # 清空输入框
            self.ui.username.clear()
            self.ui.password.clear()
            self.ui.confirm_password.clear()
            self.ui.phone.clear()
            self.ui.email.clear()
            self.ui.yanzhengma.clear()
            
            # 刷新验证码
            self.refresh_captcha()
            
            # 延迟返回登录界面
            QTimer.singleShot(1500, self.back_to_login)
            
        except Exception as e:
            logging.error(f"注册失败：{str(e)}")
            QMessageBox.warning(self, "错误", f"注册失败：{str(e)}\n请稍后重试！")
        finally:
            logging.debug("关闭数据库连接")
            self.db.close()

    def back_to_login(self):
        """返回登录界面"""
        if self.parent_window:
            self.parent_window.show()
        self.close()

class Ui_RegisterWindow(object):
    def setupUi(self, MainWindow):
        # 设置主窗口
        MainWindow.setObjectName("RegisterWindow")
        MainWindow.resize(1200, 800)
        MainWindow.setWindowTitle("注册")
        MainWindow.setFixedSize(1200, 800)
        
        # 创建中央部件
        self.centralwidget = QWidget(MainWindow)
        MainWindow.setCentralWidget(self.centralwidget)
        
        # 设置背景图片
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            background_path = os.path.join(os.path.dirname(current_dir), 'resources', 'background.png')
            if os.path.exists(background_path):
                palette = QPalette()
                image = QImage(background_path)
                if not image.isNull():
                    scaled_image = image.scaled(
                        MainWindow.size(),
                        Qt.KeepAspectRatioByExpanding,
                        Qt.SmoothTransformation
                    )
                    brush = QBrush(scaled_image)
                    palette.setBrush(QPalette.Window, brush)
                    MainWindow.setPalette(palette)
        except Exception as e:
            logging.error(f"设置背景图片失败: {str(e)}")
        
        # 创建一个半透明的白色面板
        self.register_panel = QFrame(self.centralwidget)
        self.register_panel.setGeometry(400, 100, 400, 600)
        self.register_panel.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 200);
                border-radius: 20px;
                border: 2px solid rgba(255, 255, 255, 255);
            }
        """)
        
        # 创建垂直布局
        layout = QVBoxLayout(self.register_panel)
        layout.setSpacing(25)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # 标题
        title = QLabel("用户注册")
        title.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            color: #333333;
            padding: 10px;
            background: none;
            margin: 0;
            white-space: nowrap;  /* 禁止换行 */
        """)
        title.setFixedHeight(50)  # 设置固定高度
        layout.addWidget(title)
        
        layout.addSpacing(30)
        
        # 用户名输入
        self.username = QLineEdit()
        self.username.setPlaceholderText("请输入用户名")
        self.username.setFixedHeight(45)
        layout.addWidget(self.username)
        
        # 手机号输入
        self.phone = QLineEdit()
        self.phone.setPlaceholderText("请输入手机号")
        self.phone.setFixedHeight(45)
        layout.addWidget(self.phone)
        
        # 邮箱输入
        self.email = QLineEdit()
        self.email.setPlaceholderText("请输入邮箱")
        self.email.setFixedHeight(45)
        layout.addWidget(self.email)
        
        # 密码输入
        self.password = QLineEdit()
        self.password.setPlaceholderText("请输入密码")
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setFixedHeight(45)
        layout.addWidget(self.password)
        
        # 密码强度提示
        self.password_tips = QLabel()
        self.password_tips.setStyleSheet("color: #666;")
        layout.addWidget(self.password_tips)
        
        # 确认密码输入
        self.confirm_password = QLineEdit()
        self.confirm_password.setPlaceholderText("请确认密码")
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setFixedHeight(45)
        layout.addWidget(self.confirm_password)
        
        # 验证码布局
        captcha_layout = QHBoxLayout()
        captcha_layout.setSpacing(5)  # 减小组件间距
        
        # 验证码输入框
        self.yanzhengma = QLineEdit()
        self.yanzhengma.setPlaceholderText("验证码")  # 简化提示文字
        self.yanzhengma.setFixedHeight(45)
        self.yanzhengma.setFixedWidth(80)  # 进一步减小输入框宽度
        self.yanzhengma.setStyleSheet("""
            QLineEdit {
                padding: 5px;  /* 减小内边距 */
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #4CAF50;
            }
        """)
        captcha_layout.addWidget(self.yanzhengma)
        
        # 验证码图片标签
        self.captcha_label = QLabel()
        self.captcha_label.setFixedSize(180, 45)  # 调整验证码图片宽度
        self.captcha_label.setStyleSheet("""
            QLabel {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
                padding: 2px;
            }
        """)
        captcha_layout.addWidget(self.captcha_label)
        
        # 刷新验证码按钮
        self.refresh_captcha_btn = QPushButton("刷新")
        self.refresh_captcha_btn.setFixedSize(45, 45)  # 调整刷新按钮为正方形
        self.refresh_captcha_btn.setCursor(Qt.PointingHandCursor)
        self.refresh_captcha_btn.setStyleSheet("""
            QPushButton {
                background-color: #f8f9fa;
                border: 1px solid #ddd;
                border-radius: 4px;
                color: #333;
                font-size: 12px;
                padding: 0px;  /* 移除内边距 */
            }
            QPushButton:hover {
                background-color: #e9ecef;
            }
            QPushButton:pressed {
                background-color: #dee2e6;
            }
        """)
        captcha_layout.addWidget(self.refresh_captcha_btn)
        
        # 添加弹性空间，确保组件靠左对齐
        captcha_layout.addStretch()
        
        layout.addLayout(captcha_layout)
        
        layout.addSpacing(30)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 返回按钮
        self.back_btn = QPushButton("返回登录")
        self.back_btn.setFixedSize(150, 50)
        self.back_btn.setFont(QFont("Microsoft YaHei", 13))
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #545b62;
            }
        """)
        button_layout.addWidget(self.back_btn)
        
        # 添加一些间距
        button_layout.addSpacing(20)
        
        # 注册按钮
        self.register_btn = QPushButton("注 册")
        self.register_btn.setFixedSize(150, 50)
        self.register_btn.setFont(QFont("Microsoft YaHei", 13))
        self.register_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        button_layout.addWidget(self.register_btn)
        
        layout.addLayout(button_layout)
        
        # 设置样式
        style = """
            QLineEdit {
                padding: 8px 15px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #4CAF50;
            }
        """
        MainWindow.setStyleSheet(style) 