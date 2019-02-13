import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from GenericObjectEditor import GenericObjectEditor
from PyQt5.QtCore import *
from typing import *
from Utils import Utils
from HierarchyPropertyParser import HierarchyPropertyParser

class TreeNodeButton(QPushButton):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.m_treeView=None            #type:QTreeWidget


    def showPopupMenu(self):
        if self.m_treeView is not None:
            self.m_treeView.expandAll()
            self.m_treeView.setGeometry(self.geometry().x(),self.geometry().y(),300,500)
            self.m_treeView.raise_()
            self.m_treeView.show()
            self.m_treeView.setFocus()

    def hidePopupMenu(self):
        if self.m_treeView is not None:
            self.m_treeView.hide()

    def setTree(self,tree:QTreeWidget):
        self.m_treeView=tree
        self.m_treeView.setParent(self.parent())
        self.m_treeView.resize(50,100)
        self.m_treeView.header().setVisible(False)
