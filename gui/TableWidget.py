from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from typing import *

class TableWidget(QTableWidget):
    def __init__(self,parent=None):
        super().__init__(parent)

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.RightButton:
            return
        else:
            super().mousePressEvent(e)