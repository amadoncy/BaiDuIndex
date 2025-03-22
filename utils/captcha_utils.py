import redis
import uuid
import logging
from captcha.image import ImageCaptcha
from config.redis_config import REDIS_CONFIG, CAPTCHA_CONFIG
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import io

class CaptchaManager:
    def __init__(self):
        try:
            self.redis_client = redis.Redis(**REDIS_CONFIG)
            self.image_generator = ImageCaptcha(
                width=CAPTCHA_CONFIG['width'],
                height=CAPTCHA_CONFIG['height'],
                font_sizes=(46,),  # 增大字体大小
                fonts=['arial']    # 使用简单字体
            )
        except Exception as e:
            logging.error(f"初始化验证码管理器失败: {str(e)}")
            raise

    def generate_captcha(self):
        """
        生成新的验证码
        返回: (captcha_id, QPixmap对象)
        """
        try:
            # 生成随机验证码
            import random
            import string
            chars = string.ascii_uppercase + string.digits  # 只使用大写字母和数字
            code = ''.join(random.choices(chars, k=CAPTCHA_CONFIG['length']))
            
            # 生成验证码图片
            image = self.image_generator.generate(code)
            
            # 生成唯一ID
            captcha_id = str(uuid.uuid4())
            
            # 将验证码存储到Redis
            self.redis_client.setex(
                f"verification:captcha:{captcha_id}",
                CAPTCHA_CONFIG['expire_time'],
                code.lower()
            )
            
            # 转换为QPixmap
            image_bytes = image.getvalue()
            qimage = QImage.fromData(image_bytes)
            pixmap = QPixmap.fromImage(qimage)
            
            # 调整大小以适应界面
            pixmap = pixmap.scaled(
                CAPTCHA_CONFIG['width'],
                CAPTCHA_CONFIG['height'],
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            return captcha_id, pixmap
            
        except Exception as e:
            logging.error(f"生成验证码失败: {str(e)}")
            return None, None

    def verify_captcha(self, captcha_id, user_input):
        """
        验证用户输入的验证码
        """
        try:
            # 获取存储的验证码
            redis_key = f"verification:captcha:{captcha_id}"
            stored_code = self.redis_client.get(redis_key)
            
            if not stored_code:
                return False
                
            # 验证后删除验证码
            self.redis_client.delete(redis_key)
            
            # 验证（不区分大小写）
            return user_input.lower() == stored_code.lower()
            
        except Exception as e:
            logging.error(f"验证码验证失败: {str(e)}")
            return False 