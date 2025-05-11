import re
import random
import redis
import logging
from config.redis_config import REDIS_CONFIG


class ValidationUtils:
    def __init__(self):
        self.redis_client = redis.Redis(**REDIS_CONFIG)

    def check_password_strength(self, password):
        """
        检查密码强度
        返回: (强度等级, 提示信息)
        强度等级: 0-弱, 1-中, 2-强
        """
        strength = 0
        tips = []

        # 长度检查
        if len(password) < 6:
            tips.append("密码长度至少需要6位")
        elif len(password) >= 12:
            strength += 1

        # 包含数字
        if re.search(r"\d", password):
            strength += 1
        else:
            tips.append("建议包含数字")

        # 包含字母
        if re.search(r"[a-zA-Z]", password):
            strength += 1
        else:
            tips.append("建议包含字母")

        # 包含特殊字符
        if re.search(r"[^a-zA-Z0-9]", password):
            strength += 1
        else:
            tips.append("建议包含特殊字符")

        # 计算最终强度
        if strength <= 1:
            level = 0
            if not tips:
                tips.append("密码强度较弱")
        elif strength <= 2:
            level = 1
            if not tips:
                tips.append("密码强度中等")
        else:
            level = 2
            if not tips:
                tips.append("密码强度较强")

        return level, "，".join(tips)

    def validate_phone(self, phone):
        """验证手机号格式"""
        pattern = r"^1[3-9]\d{9}$"
        return bool(re.match(pattern, phone))

    def validate_email(self, email):
        """验证邮箱格式"""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def generate_verification_code(self):
        """生成6位数字验证码"""
        return ''.join(random.choices('0123456789', k=6))

    def send_phone_code(self, phone):
        """
        发送手机验证码（模拟）
        """
        try:
            code = self.generate_verification_code()
            # 使用更有序的键名格式
            key = f"verification:phone:{phone}"
            # 将验证码存入Redis，设置5分钟过期
            self.redis_client.setex(key, 300, code)
            logging.info(f"向手机号 {phone} 发送验证码: {code}")
            return True
        except Exception as e:
            logging.error(f"发送手机验证码失败: {str(e)}")
            return False

    def send_email_code(self, email):
        """
        发送邮箱验证码（模拟）
        """
        try:
            code = self.generate_verification_code()
            # 使用更有序的键名格式
            key = f"verification:email:{email}"
            # 将验证码存入Redis，设置5分钟过期
            self.redis_client.setex(key, 300, code)
            logging.info(f"向邮箱 {email} 发送验证码: {code}")
            return True
        except Exception as e:
            logging.error(f"发送邮箱验证码失败: {str(e)}")
            return False

    def verify_phone_code(self, phone, code):
        """验证手机验证码"""
        key = f"verification:phone:{phone}"
        stored_code = self.redis_client.get(key)
        if stored_code:
            self.redis_client.delete(key)
            return stored_code == code
        return False

    def verify_email_code(self, email, code):
        """验证邮箱验证码"""
        key = f"verification:email:{email}"
        stored_code = self.redis_client.get(key)
        if stored_code:
            self.redis_client.delete(key)
            return stored_code == code
        return False