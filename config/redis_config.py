"""
Redis配置文件
"""

REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'db': 0,
    'password': None,  # 如果有密码，请设置
    'decode_responses': True
}

# 验证码配置
CAPTCHA_CONFIG = {
    'expire_time': 300,  # 验证码过期时间（秒）
    'width': 180,       # 验证码图片宽度
    'height': 45,       # 验证码图片高度
    'length': 4,        # 验证码长度
} 