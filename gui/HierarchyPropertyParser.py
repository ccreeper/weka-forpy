import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from typing import *
from Utils import Utils

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
        self.m_Root.children=[]     #type:List[HierarchyPropertyParser.TreeNode]
        self.m_Seperator="."
        self.m_Depth=0
        self.goToRoot()

    def goToChild(self,pos:int):
        if self.m_Current.children is None or pos < 0 or pos >= len(self.m_Current.children):
            sys.stderr.write("pos",str(pos))
            raise Exception("Position out of range or leaf reached")
        self.m_Current=self.m_Current.children[pos]

    def fullValue(self)->str:
        if self.m_Current == self.m_Root:
            return str(self.m_Root.value)
        else:
            return self.m_Current.context+self.m_Seperator+str(self.m_Current.value)

    def numChildren(self):
        if self.m_Current.children is None:
            return 0
        return len(self.m_Current.children)

    def getValue(self):
        return self.m_Current.value

    def goToRoot(self):
        self.m_Current=self.m_Root

    def getSeperator(self):
        return self.m_Seperator

    def goToParent(self):
        if self.m_Current.parent is not None:
            self.m_Current=self.m_Current.parent

    def build(self,p:str,delim:str):
        st=p.split(delim)
        for property in st:
            property=property.strip()
            if not self.isHierachic(property):
                return
            self.add(property)
        self.goToRoot()

    def isLeafReached(self):
        return self.m_Current.children is None

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
