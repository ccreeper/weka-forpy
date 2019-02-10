import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from typing import *
from Utils import Utils
from HierarchyPropertyParser import HierarchyPropertyParser


class TreeNodeButton(QPushButton):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.m_treeView=QTreeWidget(parent)
        self.m_treeView.setColumnCount(2)
        self.m_treeView.resize(50,100)
        self.m_treeView.header().setVisible(False)

        root = QTreeWidgetItem(self.m_treeView)
        root.setText(0, 'root')
        self.m_treeView.setColumnWidth(0, 160)

        child1 = QTreeWidgetItem(root)
        child1.setText(0, 'child1')

        child2 = QTreeWidgetItem(root)
        child2.setText(0, 'child2')

        self.m_treeView.addTopLevelItem(root)
        self.m_treeView.setVisible(False)
        self.clicked.connect(self.click)

    def focusOutEvent(self, a0: QFocusEvent):
        self.m_treeView.setVisible(False)

    def click(self):
        self.m_treeView.setGeometry(self.geometry().x(),self.geometry().y(),300,500)
        self.m_treeView.raise_()
        self.m_treeView.setVisible(True)

