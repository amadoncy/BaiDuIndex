from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox, QLabel, QLineEdit, QComboBox,
                             QDialog, QFormLayout, QDialogButtonBox)
from PyQt5.QtCore import Qt
from utils.db_utils import DatabaseConnection
import logging

class UserManagementWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("用户管理系统")
        self.setMinimumSize(800, 600)
        self.is_admin = self.check_is_admin()
        self.init_ui()
        self.load_users()

    def check_is_admin(self):
        parent = self.parent()
        username = getattr(parent, "username", None)
        if not username:
            return False
        db = DatabaseConnection()
        cursor = db.connection.cursor()
        cursor.execute("SELECT role FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        return result and result[0] == "admin"

    def init_ui(self):
        # 创建主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建按钮区域
        button_layout = QHBoxLayout()
        add_button = QPushButton("添加用户")
        add_button.clicked.connect(self.show_add_user_dialog)
        edit_button = QPushButton("编辑用户")
        edit_button.clicked.connect(self.show_edit_user_dialog)
        delete_button = QPushButton("删除用户")
        delete_button.clicked.connect(self.delete_user)
        button_layout.addWidget(add_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        if self.is_admin:
            clear_data_button = QPushButton("清空数据表")
            clear_data_button.clicked.connect(self.clear_data_tables)
            button_layout.addWidget(clear_data_button)
        button_layout.addStretch()

        # 创建用户表格
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(6)
        self.user_table.setHorizontalHeaderLabels(["ID", "用户名", "手机号", "邮箱", "角色", "创建时间"])
        self.user_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.user_table.setSelectionMode(QTableWidget.SingleSelection)

        # 添加组件到主布局
        layout.addLayout(button_layout)
        layout.addWidget(self.user_table)

    def load_users(self):
        """加载用户数据到表格"""
        try:
            db = DatabaseConnection()
            cursor = db.connection.cursor()
            cursor.execute("SELECT id, username, phone, email, role, created_at FROM users")
            users = cursor.fetchall()

            self.user_table.setRowCount(len(users))
            for row, user in enumerate(users):
                for col, value in enumerate(user):
                    item = QTableWidgetItem(str(value))
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)
                    self.user_table.setItem(row, col, item)

            self.user_table.resizeColumnsToContents()
        except Exception as e:
            logging.error(f"加载用户数据失败: {str(e)}")
            QMessageBox.critical(self, "错误", "加载用户数据失败")

    def show_add_user_dialog(self):
        """显示添加用户对话框"""
        dialog = UserDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.load_users()

    def show_edit_user_dialog(self):
        """显示编辑用户对话框"""
        selected_row = self.user_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "请先选择要编辑的用户")
            return

        user_id = self.user_table.item(selected_row, 0).text()
        username = self.user_table.item(selected_row, 1).text()
        phone = self.user_table.item(selected_row, 2).text()
        email = self.user_table.item(selected_row, 3).text()
        role = self.user_table.item(selected_row, 4).text()

        dialog = UserDialog(self, user_id, username, phone, email, role)
        if dialog.exec_() == QDialog.Accepted:
            self.load_users()

    def delete_user(self):
        """删除选中的用户"""
        selected_row = self.user_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self, "警告", "请先选择要删除的用户")
            return

        user_id = self.user_table.item(selected_row, 0).text()
        username = self.user_table.item(selected_row, 1).text()

        reply = QMessageBox.question(self, "确认删除",
                                   f"确定要删除用户 {username} 吗？",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                db = DatabaseConnection()
                cursor = db.connection.cursor()
                cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                db.connection.commit()
                self.load_users()
                QMessageBox.information(self, "成功", "用户删除成功")
            except Exception as e:
                logging.error(f"删除用户失败: {str(e)}")
                QMessageBox.critical(self, "错误", "删除用户失败")

    def clear_data_tables(self):
        """清空所有数据表，保留users、cookies、area_codes表"""
        reply = QMessageBox.question(self, "确认清空",
                                   "确定要清空所有数据表吗？此操作不可恢复！（users、cookies、area_codes表除外）",
                                   QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            try:
                db = DatabaseConnection()
                cursor = db.connection.cursor()
                # 获取所有表名
                cursor.execute("SHOW TABLES")
                tables = [table[0] for table in cursor.fetchall()]
                # 需要保留的表
                protected_tables = ['users', 'cookies', 'area_codes']
                # 清空每个表
                for table in tables:
                    if table not in protected_tables:
                        cursor.execute(f"TRUNCATE TABLE `{table}`")
                db.connection.commit()
                QMessageBox.information(self, "成功", "数据表已清空")
            except Exception as e:
                logging.error(f"清空数据表失败: {str(e)}")
                QMessageBox.critical(self, "错误", "清空数据表失败")


class UserDialog(QDialog):
    def __init__(self, parent=None, user_id=None, username="", phone="", email="", role="user"):
        super().__init__(parent)
        self.user_id = user_id
        self.setWindowTitle("添加用户" if not user_id else "编辑用户")
        self.init_ui(username, phone, email, role)

    def init_ui(self, username, phone, email, role):
        layout = QFormLayout(self)

        self.username_edit = QLineEdit(username)
        self.phone_edit = QLineEdit(phone)
        self.email_edit = QLineEdit(email)
        self.role_combo = QComboBox()
        self.role_combo.addItems(["user", "admin"])
        self.role_combo.setCurrentText(role)
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)

        layout.addRow("用户名:", self.username_edit)
        layout.addRow("手机号:", self.phone_edit)
        layout.addRow("邮箱:", self.email_edit)
        layout.addRow("角色:", self.role_combo)
        layout.addRow("密码:", self.password_edit)
        layout.addRow("确认密码:", self.confirm_password_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def accept(self):
        """验证并保存用户信息"""
        username = self.username_edit.text().strip()
        phone = self.phone_edit.text().strip()
        email = self.email_edit.text().strip()
        role = self.role_combo.currentText()
        password = self.password_edit.text()
        confirm_password = self.confirm_password_edit.text()

        if not all([username, phone, email]):
            QMessageBox.warning(self, "警告", "请填写所有必填字段")
            return

        if not self.user_id and (not password or not confirm_password):
            QMessageBox.warning(self, "警告", "请填写密码")
            return

        if password and password != confirm_password:
            QMessageBox.warning(self, "警告", "两次输入的密码不一致")
            return

        try:
            db = DatabaseConnection()
            cursor = db.connection.cursor()

            if self.user_id:  # 编辑用户
                if password:
                    cursor.execute("""
                        UPDATE users 
                        SET username = %s, phone = %s, email = %s, role = %s, password = %s
                        WHERE id = %s
                    """, (username, phone, email, role, password, self.user_id))
                else:
                    cursor.execute("""
                        UPDATE users 
                        SET username = %s, phone = %s, email = %s, role = %s
                        WHERE id = %s
                    """, (username, phone, email, role, self.user_id))
            else:  # 添加用户
                cursor.execute("""
                    INSERT INTO users (username, phone, email, role, password)
                    VALUES (%s, %s, %s, %s, %s)
                """, (username, phone, email, role, password))

            db.connection.commit()
            super().accept()
        except Exception as e:
            logging.error(f"保存用户信息失败: {str(e)}")
            QMessageBox.critical(self, "错误", "保存用户信息失败") 