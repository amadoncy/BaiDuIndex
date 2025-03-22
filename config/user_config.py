import json
import os
from pathlib import Path


class UserConfig:
    def __init__(self):
        self.config_dir = Path.home() / '.elderly_care_system'
        self.config_file = self.config_dir / 'user_config.json'
        self._ensure_config_dir()
        self.config = self._load_config()

    def _ensure_config_dir(self):
        """确保配置目录存在"""
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self):
        """加载配置文件"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def save_config(self):
        """保存配置到文件"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)

    def save_login_info(self, username, password, remember_password=False, auto_login=False):
        """保存登录信息"""
        self.config['login_info'] = {
            'username': username,
            'password': password if remember_password else '',
            'remember_password': remember_password,
            'auto_login': auto_login
        }
        self.save_config()

    def get_login_info(self):
        """获取登录信息"""
        return self.config.get('login_info', {
            'username': '',
            'password': '',
            'remember_password': False,
            'auto_login': False
        })

    def clear_login_info(self):
        """清除登录信息"""
        if 'login_info' in self.config:
            del self.config['login_info']
            self.save_config()
