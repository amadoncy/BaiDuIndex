"""
下载ECharts库脚本

此脚本检查并下载ECharts库到项目的resources目录
"""

import os
import sys

def download_echarts():
    """下载ECharts库"""
    # 确定resources目录路径
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    resources_dir = os.path.join(base_dir, "resources")
    
    # 确保resources目录存在
    if not os.path.exists(resources_dir):
        os.makedirs(resources_dir)
        print(f"创建resources目录: {resources_dir}")
    else:
        print(f"resources目录已存在: {resources_dir}")
    
    # 检查ECharts文件
    echarts_path = os.path.join(resources_dir, "echarts.min.js")
    if not os.path.exists(echarts_path):
        try:
            import requests
            print("正在从CDN下载echarts.min.js...")
            echarts_url = "https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"
            response = requests.get(echarts_url, timeout=10)
            if response.status_code == 200:
                with open(echarts_path, 'wb') as f:
                    f.write(response.content)
                print(f"成功下载并保存echarts.min.js到{echarts_path}")
                return True
            else:
                print(f"下载echarts.min.js失败，状态码: {response.status_code}")
                return False
        except Exception as e:
            print(f"下载echarts.min.js时出错: {str(e)}")
            return False
    else:
        print(f"echarts.min.js已存在: {echarts_path}")
        return True

if __name__ == "__main__":
    # 执行下载
    success = download_echarts()
    sys.exit(0 if success else 1) 