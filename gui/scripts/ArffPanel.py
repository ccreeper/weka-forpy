from typing import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from Instances import Instances
from Attributes import Attribute
from Utils import Utils
from copy import *
import threading

class ArffPanel():
    def __init__(self,table:QTableWidget):
        super().__init__()
        self.m_Table=table
        self.m_Table.verticalHeader().setVisible(False)
        self.m_Table.horizontalHeader().setFixedHeight(40)
        self.m_Table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.m_Table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.m_Table.setShowGrid(False)
        self.m_CurrentItem=None     #type:tuple

        self.m_Table.itemClicked.connect(self.selectedCombox)

    def setInstances(self,inst:Instances):
        self.m_Data=inst
        self.m_CurrentItem=None
        self.setTable(inst)

    def setTable(self,data:Instances):
        headerLabels=["No."]
        self.m_Table.setRowCount(data.numInstances())
        for column in range(data.numAttributes()):
            lab=str(column+1)+":"
            lab+=data.attribute(column).name()+'\n'
            lab+=Attribute.typeToString(data.attribute(column).type()).capitalize()
            headerLabels.append(lab)
        self.m_Table.setColumnCount(data.numAttributes()+1)
        self.m_Table.setHorizontalHeaderLabels(headerLabels)
        self.m_Table.horizontalHeader().resizeSections(QHeaderView.ResizeToContents)
        for row in range(data.numInstances()):
            item=QTableWidgetItem(str(row+1))
            self.m_Table.setItem(row,0,item)
            for column in range(data.numAttributes()):
                if data.instance(row).isMissing(column):
                    item = QTableWidgetItem("")
                    item.setBackground(QBrush(QColor(232,232,232)))
                    self.m_Table.setItem(row,column+1,item)
                    continue
                if data.attribute(column).isNominal():
                    item=QTableWidgetItem(data.attribute(column).value(data.instance(row).value(column)))
                    self.m_Table.setItem(row,column+1,item)
                else:
                    item=QTableWidgetItem(str(data.instance(row).value(column)))
                    self.m_Table.setItem(row,column+1,item)


    #TODO 失去焦点变回原来的Item
    def selectedCombox(self,item:QTableWidgetItem):
        if self.m_CurrentItem is not None:
            # newItem=QTableWidgetItem(self.m_Data.attribute(self.m_CurrentItem[1]-1).value(self.m_Data.instance(self.m_CurrentItem[0]).value(self.m_CurrentItem[1]-1)))
            widget=self.m_Table.cellWidget(self.m_CurrentItem[0],self.m_CurrentItem[1])
            newItem=QTableWidgetItem(widget.currentText())
            if widget.currentIndex()==0:
                newItem.setBackground(QBrush(QColor(232,232,232)))
            self.m_Table.removeCellWidget(self.m_CurrentItem[0],self.m_CurrentItem[1])
            self.m_Table.setItem(self.m_CurrentItem[0],self.m_CurrentItem[1],newItem)
            self.m_CurrentItem=None
        if item.column() == 0:
            return
        if self.m_Data.attribute(item.column()-1).isNominal():
            newItem=QComboBox()
            newItem.addItem("")
            newItem.addItems(self.m_Data.attribute(item.column()-1).values())
            if self.m_Data.instance(item.row()).isMissing(item.column()-1):
                newItem.setCurrentIndex(0)
            else:
                newItem.setCurrentIndex(self.m_Data.instance(item.row()).value(item.column()-1)+1)
            self.m_Table.setCellWidget(item.row(),item.column(),newItem)
            self.m_CurrentItem=(item.row(),item.column())
            newItem.showPopup()
        else:
            self.m_CurrentItem=None