from PyQt5.QtWidgets import QWidget, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView
from pyecharts.render import make_snapshot
from tempfile import NamedTemporaryFile
import os

class ChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        # 创建WebView来显示图表
        self.web_view = QWebEngineView()
        layout.addWidget(self.web_view)
        
        # 设置默认大小
        self.setMinimumSize(800, 400)

    def update_chart(self, chart):
        """更新图表"""
        try:
            # 创建临时文件来保存图表
            with NamedTemporaryFile(suffix='.html', delete=False) as tmp:
                chart.render(tmp.name)
                self.web_view.setUrl(f'file:///{tmp.name}')
                
        except Exception as e:
            print(f"更新图表时出错: {str(e)}")
            import traceback
            print(f"错误详情: {traceback.format_exc()}") 