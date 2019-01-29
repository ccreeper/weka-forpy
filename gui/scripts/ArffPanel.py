from typing import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from Instances import Instances
from Attributes import Attribute
import tempfile
import pickle
from Utils import Utils
from copy import *
import threading

class ArffPanel(QAbstractItemModel):
    def __init__(self,table:QTableWidget):
        super().__init__()
        self.m_Table=table
        self.initalize()
        self.setTable()
        self.createMenu()
        self.attachMenuItemListener()

    def initalize(self):
        #可能没用
        self.m_Filename=""
        self.m_Title=""
        #end
        #当前选中的列
        self.m_CurrentCol = -1
        self.m_LastSearch = ""
        self.m_LastReplace = ""
        self.m_ShowAttributeIndex = True
        self.m_Changed = False
        self.m_ChangeListeners = set()
        self.m_CurrentCombobox=None     #type:tuple
        self.model=ArffModel()

    def attachMenuItemListener(self):
        self.model.delete_instance_signal.connect(self.deleteInstanceEvent)


    def setTable(self):
        self.m_Table.verticalHeader().setVisible(False)
        self.m_Table.horizontalHeader().setFixedHeight(40)
        self.m_Table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.m_Table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.m_Table.setShowGrid(False)
        self.m_Table.itemClicked.connect(self.selectedCombox)
        #单元格菜单
        self.m_Table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.m_Table.customContextMenuRequested.connect(self.generateMenu)
        #表头菜单
        self.m_Table.horizontalHeader().setContextMenuPolicy(Qt.CustomContextMenu)
        self.m_Table.horizontalHeader().customContextMenuRequested.connect(self.generateHeaderMenu)

    def createMenu(self):
        self.headerMenu=QMenu()
        self.setAllValuesToMenuItem=self.headerMenu.addAction(u'Set all values to...')
        self.setMissingValuesToMenuItem=self.headerMenu.addAction(u'Set missing values to...')
        self.renameAttributeMenuItem=self.headerMenu.addAction(u'Rename attribute')
        self.deleteAttributeMenuItem=self.headerMenu.addAction(u'Delete attribute')
        self.deleteAttributesMenuItem=self.headerMenu.addAction(u'Delete attributes')
        self.optimalColumnWidthMenuItem=self.headerMenu.addAction(u'Optimal column width')

        self.tableMenu=QMenu()
        self.searchMenuItem=self.tableMenu.addAction(u'Search')
        self.deleteSelectedInstanceMenuItem=self.tableMenu.addAction(u'Delete selected instance')
        self.insertNewInstanceMenuItem=self.tableMenu.addAction(u'Insert new instance')


    def setMenu(self):
        isNull=self.model.getInstance() is None
        hasColumns=not isNull and self.model.getInstance().numAttributes()>0
        hasRows=not isNull and self.model.getInstance().numInstances()>0
        attSelected=hasRows and self.model.isAttribute(self.m_CurrentCol)
        isNumeric=attSelected and self.model.getAttributeAt(self.m_CurrentCol).isNumeric()

        self.searchMenuItem.setEnabled(True)
        self.setAllValuesToMenuItem.setEnabled(attSelected)
        self.setMissingValuesToMenuItem.setEnabled(attSelected)
        self.renameAttributeMenuItem.setEnabled(attSelected)
        self.deleteAttributeMenuItem.setEnabled(attSelected)
        self.deleteAttributesMenuItem.setEnabled(attSelected)
        self.deleteSelectedInstanceMenuItem.setEnabled(hasRows and self.m_Table.currentItem() is not None)

    def setInstances(self,inst:Instances):
        #封装数据实体
        self.model.setInstance(inst)
        #目前被选择的下拉框row,column
        self.m_CurrentCombobox=None     #tyep:tuple
        self.setModel(inst)
        self.model.clearUndo()
        self.m_Changed=False


    def setModel(self,data:Instances):
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
            self.m_Table.setRowHeight(row,30)


    #TODO 失去焦点变回原来的Item
    def selectedCombox(self,item:QTableWidgetItem):
        if self.m_CurrentCombobox is not None:
            # newItem=QTableWidgetItem(self.m_Data.attribute(self.m_CurrentItem[1]-1).value(self.m_Data.instance(self.m_CurrentItem[0]).value(self.m_CurrentItem[1]-1)))
            widget=self.m_Table.cellWidget(self.m_CurrentCombobox[0], self.m_CurrentCombobox[1])
            newItem=QTableWidgetItem(widget.currentText())
            if widget.currentIndex()==0:
                newItem.setBackground(QBrush(QColor(232,232,232)))
            self.m_Table.removeCellWidget(self.m_CurrentCombobox[0], self.m_CurrentCombobox[1])
            self.m_Table.setItem(self.m_CurrentCombobox[0], self.m_CurrentCombobox[1], newItem)
            self.m_CurrentCombobox=None
        if item.column() == 0:
            return
        if self.model.getInstance().attribute(item.column()-1).isNominal():
            newItem=QComboBox()
            newItem.addItem("")
            newItem.addItems(self.model.getInstance().attribute(item.column()-1).values())
            if self.model.getInstance().instance(item.row()).isMissing(item.column()-1):
                newItem.setCurrentIndex(0)
            else:
                newItem.setCurrentIndex(self.model.getInstance().instance(item.row()).value(item.column()-1)+1)
            self.m_Table.setCellWidget(item.row(),item.column(),newItem)
            self.m_CurrentCombobox=(item.row(), item.column())
            newItem.showPopup()
        else:
            self.m_CurrentCombobox=None

    def generateMenu(self,pos):
        action=self.tableMenu.exec_(self.m_Table.cursor().pos())
        if action == self.searchMenuItem:
            pass
        elif action == self.deleteSelectedInstanceMenuItem:
            self.deleteInstance()
        elif action == self.insertNewInstanceMenuItem:
            pass
        else:
            return


    def generateHeaderMenu(self,pos):
        action=self.headerMenu.exec_(self.m_Table.cursor().pos())
        if action == self.setAllValuesToMenuItem:
            pass
        elif action == self.setMissingValuesToMenuItem:
            pass
        elif action == self.renameAttributeMenuItem:
            pass
        elif action == self.deleteAttributeMenuItem:
            pass
        elif action == self.deleteAttributesMenuItem:
            pass
        elif action == self.optimalColumnWidthMenuItem:
            pass
        else:
            return


    def deleteInstance(self):
        item=self.m_Table.currentItem()
        if item is None:
            return
        self.model.deleteInstanceAt(item.row())

    def deleteInstanceEvent(self,row:int):
        self.m_Table.removeRow(row)
        Utils.debugOut("delete_position:",row)
        Utils.debugOut("delete_after_rowCount:",self.m_Table.rowCount())
        for i in range(row,self.m_Table.rowCount()):
            self.m_Table.item(i,0).setText(str(i+1))




class ArffModel(QObject):
    delete_instance_signal=pyqtSignal(int)
    def __init__(self,data:Instances=None):
        super().__init__()
        self.m_Data=data
        self.m_UndoList=[]      #type:List

    def setInstance(self,data:Instances):
        self.m_Data=data

    def clearUndo(self):
        self.m_UndoList.clear()

    def getInstance(self):
        return self.m_Data

    def isAttribute(self,columnIndex:int):
        return columnIndex>0 and columnIndex<self.m_Data.numAttributes()+1

    def getAttributeAt(self,columnIndex:int):
        if self.isAttribute(columnIndex):
            return self.m_Data.attribute(columnIndex-1)


    def deleteInstanceAt(self,rowIndex:int):
        if rowIndex<self.m_Data.numInstances():
            self.addUndoPoint()
            self.m_Data.delete(rowIndex)
            self.delete_instance_signal.emit(rowIndex)

    def addUndoPoint(self):
        if self.m_Data is not None:
            temp=tempfile.TemporaryFile()
            pickle.dump(self.m_Data,temp)
            temp.seek(0)
            self.m_UndoList.append(temp)

