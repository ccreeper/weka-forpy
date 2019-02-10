from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from HierarchyPropertyParser import HierarchyPropertyParser
from Capabilities import Capabilities
from CapabilitiesHandler import CapabilitiesHandler
from Utils import Utils
from typing import *

class TreeList(QTreeWidget):
    def __init__(self,hpps:Dict[str,HierarchyPropertyParser],parent=None):
        super().__init__(parent)
        if len(hpps) >1:
            superRoot=GOETreeNode("root")
        else:
            superRoot=None
        for hpp in hpps.values():
            hpp.goToRoot()
            root=GOETreeNode(hpp.getValue())
            self.

    def addChildrenToTree(self,tree:'GOETreeNode',hpp:HierarchyPropertyParser):
        for i in range(hpp.numChildren()):
            hpp.goToChild(i)
            child = GOETreeNode(hpp.getValue())
            if self.m_





class GOETreeNode(QTreeWidgetItem):
    NO_SUPPORT = "silver"
    MAYBE_SUPPORT = "blue"
    def __init__(self,text,parent=None):
        super().__init__(parent)
        self.m_Capabilities=None        #type:Capabilities
        self.setText(0,text)

    #TODO
    def __str__(self):pass


    def initCapabilities(self):
        if self.m_Capabilities is not None:
            return
        if self.isLeaf():
            return
        classname=self.getClassnameFromPath(self)
        cls=Utils.loadClassForName(classname)
        if not issubclass(cls,CapabilitiesHandler):
            return
        obj=cls()
        self.m_Capabilities=obj.getCapabilities()



    def getClassnameFromPath(self,node:QTreeWidgetItem):
        namePath=[]
        while node is not None:
            namePath.append(node.text(0))
            node=node.parent()
        namePath.reverse()
        classname='.'.join(namePath)
        return classname


    def isLeaf(self):
        return self.childCount()==0