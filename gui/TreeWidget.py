from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *

class TreeWidget(QTreeWidget):
    def __init__(self,parent=None):
        super().__init__(parent)

    def focusOutEvent(self, e: QFocusEvent):
        self.hide()