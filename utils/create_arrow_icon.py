from PIL import Image, ImageDraw
import os

def create_down_arrow():
    # 创建一个24x24的透明背景图像
    img = Image.new('RGBA', (24, 24), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 绘制白色箭头
    points = [(6, 8), (12, 16), (18, 8)]  # 三角形的三个顶点
    draw.polygon(points, fill='white')
    
    # 确保resources目录存在
    resources_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')
    if not os.path.exists(resources_dir):
        os.makedirs(resources_dir)
    
    # 保存图标
    icon_path = os.path.join(resources_dir, 'down_arrow.png')
    img.save(icon_path, 'PNG')
    print(f"下拉箭头图标已创建：{icon_path}")

if __name__ == '__main__':
    create_down_arrow() 