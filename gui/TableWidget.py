from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from Instances import Instances,Instance
from typing import *

class TableWidget(QTableWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.m_LastSearch=""
        self.m_CurrentSelectedRow=None          #tip:range start with 0
        self.m_IsMenuClick=False

    def mousePressEvent(self, e: QMouseEvent):
        if e.button() == Qt.RightButton:
            return
        elif e.button() == Qt.LeftButton:
            if not self.m_IsMenuClick:
                super().mousePressEvent(e)
                self.m_CurrentSelectedRow=self.currentItem().row()
            self.setMenuClickNow(False)
        else:
            super().mousePressEvent(e)

    def setSearchString(self,searchString:str):
        items=self.findItems(searchString,Qt.MatchExactly | Qt.MatchCaseSensitive)
        for item in items:
            item.setBackground(QBrush(Qt.red))
        items=self.findItems(self.m_LastSearch,Qt.MatchCaseSensitive | Qt.MatchExactly)
        for item in items:
            item.setBackground(QBrush(Qt.white))
        self.m_LastSearch=searchString

    def getSelectedRow(self):
        return self.m_CurrentSelectedRow

    def setMenuClickNow(self,flag:bool):
        self.m_IsMenuClick=flag

    def setRawItem(self,inst:Instances,row:int):
        for column in range(inst.numAttributes()):
            if inst.instance(row).isMissing(column):
                item = QTableWidgetItem("")
                item.setBackground(QBrush(QColor(232, 232, 232)))
                self.setItem(row, column + 1, item)
                continue
            if inst.attribute(column).isNominal():
                item = QTableWidgetItem(inst.attribute(column).value(inst.instance(row).value(column)))
                self.setItem(row, column + 1, item)
            else:
                item = QTableWidgetItem(str(inst.instance(row).value(column)))
                self.setItem(row, column + 1, item)