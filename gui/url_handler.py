"""
URL处理工具 - 兼容版本

此文件包含处理WebEngine URL变化的函数，用于检测并响应热力图加载失败等情况。
"""

def handle_url_changed(self, url):
    """处理URL变化事件"""
    url_str = url.toString()
    print(f"URL变化: {url_str}")
    
    # 检查是否包含fallback参数，表示热力图加载失败
    if "fallback=true" in url_str:
        print("检测到热力图加载失败，切换到表格视图")
        try:
            if hasattr(self, 'region_view_selector'):
                # 切换到表格视图
                print("切换到表格视图")
                self.region_view_selector.setCurrentIndex(0)
        except Exception as e:
            print(f"切换视图出错: {e}") 