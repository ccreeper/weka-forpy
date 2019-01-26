from typing import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from Instances import Instances
from Attributes import Attribute

class ArffPanel():
    def __init__(self,table:QTableWidget):
        self.m_Table=table
        self.m_Table.verticalHeader().setVisible(False)
        self.m_Table.horizontalHeader().setFixedHeight(40)
        self.m_Table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.m_Table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.m_Table.setShowGrid(False)

    def setInstances(self,inst:Instances):
        self.setTable(inst)

    def setTable(self,data:Instances):
        headerLabels=["No."]
        for i in range(data.numAttributes()):
            lab=str(i+1)+":"
            lab+=data.attribute(i).name()+'\n'
            lab+=Attribute.typeToString(data.attribute(i).type()).capitalize()
            headerLabels.append(lab)
        self.m_Table.setColumnCount(data.numAttributes())
        self.m_Table.setHorizontalHeaderLabels(headerLabels)
        self.m_Table.horizontalHeader().resizeSections(QHeaderView.ResizeToContents)