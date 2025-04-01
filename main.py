import sys
import collections.abc
sys.modules['collections'].Iterable = collections.abc.Iterable
print("已修复collections.Iterable导入问题")

from PyQt5.QtWidgets import QApplication
from gui.loginwindow import LoginWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())