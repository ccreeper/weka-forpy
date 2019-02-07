import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from typing import *
from Utils import Utils


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

class HierarchyPropertyParser():
    class TreeNode():
        def __init__(self):
            self.parent=None    #type:HierarchyPropertyParser.TreeNode
            self.value=None     #type:str
            self.children=None       #type:List[HierarchyPropertyParser.TreeNode]
            self.level=0
            self.context=None        #type:str

    def __init__(self):
        self.m_Root=self.TreeNode()
        self.m_Root.parent=None
        self.m_Root.children=[]
        self.m_Seperator="."
        self.m_Depth=0
        self.goToRoot()


    def goToRoot(self):
        self.m_Current=self.m_Root

    def getSeperator(self):
        return self.m_Seperator

    def build(self,p:str,delim:str):
        st=p.split(delim)
        for property in st:
            property=property.strip()
            if not self.isHierachic(property):
                return
            self.add(property)
        self.goToRoot()

    def isHierachic(self,string:str):
        try:
            index=string.index(self.m_Seperator)
            if index == len(string)-1:
                return False
            return True
        except ValueError:
            return False

    def add(self,property:str):
        values=self.tokenize(property)
        if self.m_Root.value is None:
            self.m_Root.value=values[0]
        self.buildBranch(self.m_Root,values,1)

    def tokenize(self,rawString:str):
        result=[]
        tk=rawString.split(self.m_Seperator)
        for element in tk:
            result.append(element)
        return result

    def buildBranch(self,parent:TreeNode,values:List[str],lvl:int):
        if lvl == len(values):
            parent.children = None
            return
        if lvl > (self.m_Depth-1):
            self.m_Depth=lvl+1
        kids=parent.children
        index=self.search(kids,values[lvl])
        if index != -1:
            newParent=kids[index]
            if newParent.children is None:
                newParent.children=[]
            self.buildBranch(newParent,values,lvl+1)
        else:
            added=self.TreeNode()
            added.parent=parent
            added.value=values[lvl]
            added.children=[]
            added.level=lvl
            if parent != self.m_Root:
                added.context=parent.context+self.m_Seperator+parent.value
            else:
                added.context=parent.value
            kids.append(added)
            self.buildBranch(added,values,lvl+1)

    def search(self,vct:List[TreeNode],target:str):
        if vct is None:
            return -1
        for i in range(len(vct)):
            if target == vct[i].value:
                return i
        return -1

    def contains(self,string:str):
        item=string.split(self.m_Seperator)
        if item[0] != self.m_Root.value:
            return False
        return self.isContained(self.m_Root,item,1)

    def isContained(self,parent:TreeNode,values:List[str],lvl:int):
        if lvl == len(values):
            return True
        elif lvl > len(values):
            return  False
        else:
            kids=parent.children
            index=self.search(kids,values[lvl])
            if index != -1:
                newParent=kids[index]
                return self.isContained(newParent,values,lvl+1)
            else:
                return False
