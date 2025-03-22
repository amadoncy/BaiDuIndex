from PyQt5.QtWidgets import (QWidget, QLineEdit, QPushButton, 
                             QVBoxLayout, QHBoxLayout, QLabel, QTabWidget,
                             QMainWindow, QMessageBox, QFrame, QComboBox, QStackedWidget)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QBrush, QImage, QIcon
import os
import logging
from utils.db_utils import DatabaseConnection
from utils.validation_utils import ValidationUtils

class ResetPasswordWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__()  # 移除parent参数
        self.parent_window = parent  # 保存父窗口引用
        # 设置窗口图标
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources', 'logo.png')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        self.ui = Ui_ResetPasswordWindow()
        self.ui.setupUi(self)
        self.db = DatabaseConnection()
        self.validation = ValidationUtils()
        
        # 初始化计时器
        self.phone_timer = QTimer(self)
        self.email_timer = QTimer(self)
        self.phone_countdown = 60
        self.email_countdown = 60
        self.phone_timer.timeout.connect(self.update_phone_timer)
        self.email_timer.timeout.connect(self.update_email_timer)
        
        # 绑定下拉框切换事件
        self.ui.method_combo.currentIndexChanged.connect(self.on_method_changed)
        
        # 绑定按钮事件
        self.ui.phone_send_btn.clicked.connect(lambda: self.send_code('phone'))
        self.ui.email_send_btn.clicked.connect(lambda: self.send_code('email'))
        self.ui.phone_reset_btn.clicked.connect(lambda: self.reset_password('phone'))
        self.ui.email_reset_btn.clicked.connect(lambda: self.reset_password('email'))
        self.ui.back_btn.clicked.connect(self.back_to_login)
        
        # 绑定密码输入事件
        self.ui.phone_new_password.textChanged.connect(lambda: self.check_password_strength('phone'))
        self.ui.email_new_password.textChanged.connect(lambda: self.check_password_strength('email'))

    def update_phone_timer(self):
        """更新手机验证码按钮倒计时"""
        self.phone_countdown -= 1
        if self.phone_countdown <= 0:
            self.phone_timer.stop()
            self.ui.phone_send_btn.setEnabled(True)
            self.ui.phone_send_btn.setText("发送验证码")
            self.phone_countdown = 60
        else:
            self.ui.phone_send_btn.setText(f"重新发送({self.phone_countdown})")

    def update_email_timer(self):
        """更新邮箱验证码按钮倒计时"""
        self.email_countdown -= 1
        if self.email_countdown <= 0:
            self.email_timer.stop()
            self.ui.email_send_btn.setEnabled(True)
            self.ui.email_send_btn.setText("发送验证码")
            self.email_countdown = 60
        else:
            self.ui.email_send_btn.setText(f"重新发送({self.email_countdown})")

    def on_method_changed(self, index):
        """处理找回方式切换"""
        self.ui.stack_widget.setCurrentIndex(index)

    def send_code(self, mode):
        """发送验证码"""
        if mode == 'phone':
            phone = self.ui.phone_input.text().strip()
            if not phone:
                QMessageBox.warning(self, "警告", "请输入手机号！")
                return
            if not self.validation.validate_phone(phone):
                QMessageBox.warning(self, "警告", "手机号格式不正确！")
                return
                
            # 检查手机号是否存在
            if not self.check_exists('phone', phone):
                QMessageBox.warning(self, "警告", "该手机号未注册！")
                return
                
            if self.validation.send_phone_code(phone):
                QMessageBox.information(self, "成功", "验证码已发送，请查收！")
                # 开始倒计时
                self.ui.phone_send_btn.setEnabled(False)
                self.phone_timer.start(1000)  # 每秒触发一次
                self.ui.phone_send_btn.setText(f"重新发送({self.phone_countdown})")
            else:
                QMessageBox.warning(self, "错误", "验证码发送失败，请稍后重试！")
                
        else:  # email
            email = self.ui.email_input.text().strip()
            if not email:
                QMessageBox.warning(self, "警告", "请输入邮箱！")
                return
            if not self.validation.validate_email(email):
                QMessageBox.warning(self, "警告", "邮箱格式不正确！")
                return
                
            # 检查邮箱是否存在
            if not self.check_exists('email', email):
                QMessageBox.warning(self, "警告", "该邮箱未注册！")
                return
                
            if self.validation.send_email_code(email):
                QMessageBox.information(self, "成功", "验证码已发送，请查收！")
                # 开始倒计时
                self.ui.email_send_btn.setEnabled(False)
                self.email_timer.start(1000)  # 每秒触发一次
                self.ui.email_send_btn.setText(f"重新发送({self.email_countdown})")
            else:
                QMessageBox.warning(self, "错误", "验证码发送失败，请稍后重试！")

    def check_exists(self, field, value):
        """检查手机号或邮箱是否存在"""
        try:
            logging.info(f"开始检查{field}是否存在: {value}")
            if not self.db.connect():
                logging.error("数据库连接失败")
                return False
                
            logging.info("数据库连接成功")
            
            query = f"SELECT id FROM users WHERE {field} = %s"
            logging.info(f"执行查询: {query}, 参数: {value}")
            
            self.db.cursor.execute(query, (value,))
            result = self.db.cursor.fetchone()
            
            if result:
                logging.info(f"找到匹配的{field}记录")
                return True
            else:
                logging.warning(f"未找到匹配的{field}记录")
                return False
                
        except Exception as e:
            logging.error(f"检查{field}是否存在失败：{str(e)}")
            return False
        finally:
            logging.info("关闭数据库连接")
            self.db.close()

    def check_password_strength(self, mode):
        """检查密码强度"""
        password = self.ui.phone_new_password.text() if mode == 'phone' else self.ui.email_new_password.text()
        level, tips = self.validation.check_password_strength(password)
        
        # 设置提示文字颜色
        color = "#dc3545" if level == 0 else "#ffc107" if level == 1 else "#28a745"
        style = f"color: {color};"
        
        if mode == 'phone':
            self.ui.phone_password_tips.setStyleSheet(style)
            self.ui.phone_password_tips.setText(tips)
        else:
            self.ui.email_password_tips.setStyleSheet(style)
            self.ui.email_password_tips.setText(tips)

    def reset_password(self, mode):
        """重置密码"""
        try:
            if mode == 'phone':
                phone = self.ui.phone_input.text().strip()
                code = self.ui.phone_code.text().strip()
                password = self.ui.phone_new_password.text()
                confirm_password = self.ui.phone_confirm_password.text()
                
                if not all([phone, code, password, confirm_password]):
                    QMessageBox.warning(self, "警告", "请填写所有必填项！")
                    return
                    
                if not self.validation.verify_phone_code(phone, code):
                    QMessageBox.warning(self, "错误", "验证码错误或已过期！")
                    return
                    
                if password != confirm_password:
                    QMessageBox.warning(self, "警告", "两次输入的密码不一致！")
                    return
                    
                # 更新密码
                if self.update_password('phone', phone, password):
                    QMessageBox.information(self, "成功", "密码重置成功！")
                    if self.parent_window:
                        self.parent_window.show()
                    self.close()
                else:
                    QMessageBox.warning(self, "错误", "密码重置失败，请稍后重试！")
                    
            else:  # email
                email = self.ui.email_input.text().strip()
                code = self.ui.email_code.text().strip()
                password = self.ui.email_new_password.text()
                confirm_password = self.ui.email_confirm_password.text()
                
                if not all([email, code, password, confirm_password]):
                    QMessageBox.warning(self, "警告", "请填写所有必填项！")
                    return
                    
                if not self.validation.verify_email_code(email, code):
                    QMessageBox.warning(self, "错误", "验证码错误或已过期！")
                    return
                    
                if password != confirm_password:
                    QMessageBox.warning(self, "警告", "两次输入的密码不一致！")
                    return
                    
                # 更新密码
                if self.update_password('email', email, password):
                    QMessageBox.information(self, "成功", "密码重置成功！")
                    if self.parent_window:
                        self.parent_window.show()
                    self.close()
                else:
                    QMessageBox.warning(self, "错误", "密码重置失败，请稍后重试！")
        except Exception as e:
            logging.error(f"重置密码时发生错误：{str(e)}")
            QMessageBox.warning(self, "错误", "重置密码失败，请稍后重试！")

    def update_password(self, field, value, new_password):
        """更新密码"""
        try:
            if self.db.connect():
                # 确保密码是字符串类型
                new_password = str(new_password)
                query = f"UPDATE users SET password = %s WHERE {field} = %s"
                self.db.cursor.execute(query, (new_password, value))
                self.db.connection.commit()
                return True
        except Exception as e:
            logging.error(f"更新密码失败：{str(e)}")
        finally:
            self.db.close()
        return False

    def back_to_login(self):
        """返回登录界面"""
        if self.parent_window:
            self.parent_window.show()
        self.close()

class Ui_ResetPasswordWindow(object):
    def setupUi(self, MainWindow):
        # 设置主窗口
        MainWindow.setObjectName("ResetPasswordWindow")
        MainWindow.resize(1200, 800)
        MainWindow.setWindowTitle("找回密码")
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
        self.reset_panel = QFrame(self.centralwidget)
        self.reset_panel.setGeometry(400, 100, 400, 600)
        self.reset_panel.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 200);
                border-radius: 20px;
                border: 2px solid rgba(255, 255, 255, 255);
            }
        """)
        
        # 创建垂直布局
        layout = QVBoxLayout(self.reset_panel)
        layout.setSpacing(25)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # 标题
        title = QLabel("找回密码")
        title.setFont(QFont("Microsoft YaHei", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            color: #333333;
            padding: 10px;
            background: none;
            margin: 0;
            white-space: nowrap;
        """)
        title.setFixedHeight(50)
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # 找回方式选择
        method_layout = QHBoxLayout()
        method_label = QLabel("找回方式：")
        method_label.setFont(QFont("Microsoft YaHei", 12))
        method_layout.addWidget(method_label)
        
        self.method_combo = QComboBox()
        self.method_combo.addItems(["手机号找回", "邮箱找回"])
        self.method_combo.setFixedHeight(35)
        self.method_combo.setFont(QFont("Microsoft YaHei", 12))
        self.method_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px 10px;
                background: white;
            }
            QComboBox:hover {
                border: 1px solid #4CAF50;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: url(down_arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        method_layout.addWidget(self.method_combo)
        layout.addLayout(method_layout)
        
        # 创建堆叠部件
        self.stack_widget = QStackedWidget()
        
        # 手机号找回页面
        phone_page = QWidget()
        phone_layout = QVBoxLayout(phone_page)
        phone_layout.setSpacing(20)
        
        # 手机号输入
        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("请输入手机号")
        self.phone_input.setFixedHeight(45)
        phone_layout.addWidget(self.phone_input)
        
        # 手机验证码布局
        phone_code_layout = QHBoxLayout()
        self.phone_code = QLineEdit()
        self.phone_code.setPlaceholderText("请输入验证码")
        self.phone_code.setFixedHeight(45)
        phone_code_layout.addWidget(self.phone_code)
        
        self.phone_send_btn = QPushButton("发送验证码")
        self.phone_send_btn.setFixedSize(100, 45)
        self.phone_send_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        phone_code_layout.addWidget(self.phone_send_btn)
        phone_layout.addLayout(phone_code_layout)
        
        # 新密码输入
        self.phone_new_password = QLineEdit()
        self.phone_new_password.setPlaceholderText("请输入新密码")
        self.phone_new_password.setEchoMode(QLineEdit.Password)
        self.phone_new_password.setFixedHeight(45)
        phone_layout.addWidget(self.phone_new_password)
        
        # 密码强度提示
        self.phone_password_tips = QLabel()
        self.phone_password_tips.setStyleSheet("color: #666;")
        phone_layout.addWidget(self.phone_password_tips)
        
        # 确认密码输入
        self.phone_confirm_password = QLineEdit()
        self.phone_confirm_password.setPlaceholderText("请确认新密码")
        self.phone_confirm_password.setEchoMode(QLineEdit.Password)
        self.phone_confirm_password.setFixedHeight(45)
        phone_layout.addWidget(self.phone_confirm_password)
        
        # 重置按钮
        self.phone_reset_btn = QPushButton("重置密码")
        self.phone_reset_btn.setFixedHeight(45)
        self.phone_reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        phone_layout.addWidget(self.phone_reset_btn)
        phone_layout.addStretch()
        
        # 邮箱找回页面
        email_page = QWidget()
        email_layout = QVBoxLayout(email_page)
        email_layout.setSpacing(20)
        
        # 邮箱输入
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("请输入邮箱")
        self.email_input.setFixedHeight(45)
        email_layout.addWidget(self.email_input)
        
        # 邮箱验证码布局
        email_code_layout = QHBoxLayout()
        self.email_code = QLineEdit()
        self.email_code.setPlaceholderText("请输入验证码")
        self.email_code.setFixedHeight(45)
        email_code_layout.addWidget(self.email_code)
        
        self.email_send_btn = QPushButton("发送验证码")
        self.email_send_btn.setFixedSize(100, 45)
        self.email_send_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        email_code_layout.addWidget(self.email_send_btn)
        email_layout.addLayout(email_code_layout)
        
        # 新密码输入
        self.email_new_password = QLineEdit()
        self.email_new_password.setPlaceholderText("请输入新密码")
        self.email_new_password.setEchoMode(QLineEdit.Password)
        self.email_new_password.setFixedHeight(45)
        email_layout.addWidget(self.email_new_password)
        
        # 密码强度提示
        self.email_password_tips = QLabel()
        self.email_password_tips.setStyleSheet("color: #666;")
        email_layout.addWidget(self.email_password_tips)
        
        # 确认密码输入
        self.email_confirm_password = QLineEdit()
        self.email_confirm_password.setPlaceholderText("请确认新密码")
        self.email_confirm_password.setEchoMode(QLineEdit.Password)
        self.email_confirm_password.setFixedHeight(45)
        email_layout.addWidget(self.email_confirm_password)
        
        # 重置按钮
        self.email_reset_btn = QPushButton("重置密码")
        self.email_reset_btn.setFixedHeight(45)
        self.email_reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        email_layout.addWidget(self.email_reset_btn)
        email_layout.addStretch()
        
        # 添加页面到堆叠部件
        self.stack_widget.addWidget(phone_page)
        self.stack_widget.addWidget(email_page)
        layout.addWidget(self.stack_widget)
        
        # 返回按钮
        self.back_btn = QPushButton("返回登录")
        self.back_btn.setFixedHeight(45)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        layout.addWidget(self.back_btn)
        
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