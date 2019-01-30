from typing import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from Instances import Instances,Instance
from Attributes import Attribute
import tempfile
import pickle
from Utils import Utils
from TableWidget import TableWidget
from copy import *
from InsertInstanceDialog import InserInstanceDialog
import threading

class ArffPanel(QAbstractItemModel):
    def __init__(self,table:QTableWidget):
        super().__init__()
        self.m_Table=table      #type:TableWidget
        self.initalize()
        self.setTable()
        self.createMenu()
        self.setMenu()
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
        self.model.insert_instance_signal.connect(self.insertInstanceEvent)


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
        self.clearSearchMenuItem=self.tableMenu.addAction(u'Clear search')
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
        ###test
        # try:
        #     for row in range(data.numInstances()):
        #         print(data.instance(row).m_Data)
        # except AttributeError:
        #     print("Row:",row)
        ###
        for row in range(data.numInstances()):
            item=QTableWidgetItem(str(row+1))
            self.m_Table.setItem(row,0,item)
            self.m_Table.setRawItem(data,row)
            self.m_Table.setRowHeight(row,30)


    #TODO 失去焦点变回原来的Item
    def selectedCombox(self,item:QTableWidgetItem):
        if self.m_CurrentCombobox is not None:
            # newItem=QTableWidgetItem(self.m_Data.attribute(self.m_CurrentItem[1]-1).value(self.m_Data.instance(self.m_CurrentItem[0]).value(self.m_CurrentItem[1]-1)))
            widget=self.m_Table.cellWidget(self.m_CurrentCombobox[0], self.m_CurrentCombobox[1])
            newItem=QTableWidgetItem(widget.currentText())
            if widget.currentText()=="":
                newItem.setBackground(QBrush(QColor(232,232,232)))
            elif widget.currentText()==self.m_LastSearch:
                newItem.setBackground(QBrush(Qt.red))
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

    #表格菜单
    def generateMenu(self,pos):
        self.m_Table.setMenuClickNow(True)
        Utils.debugOut("currentSelectedRow:",self.m_Table.getSelectedRow())
        action=self.tableMenu.exec_(self.m_Table.cursor().pos())
        if action == self.searchMenuItem:
            self.search()
        elif action == self.clearSearchMenuItem:
            self.clearSearch()
        elif action == self.deleteSelectedInstanceMenuItem:
            self.deleteInstance()
        elif action == self.insertNewInstanceMenuItem:
            self.addInstance()
        else:
            return
        self.m_Table.setMenuClickNow(False)

    #表头菜单
    def generateHeaderMenu(self,pos):
        self.m_Table.setMenuClickNow(True)
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
        self.m_Table.setMenuClickNow(False)

    #删除选中的实例
    def deleteInstance(self):
        item=self.m_Table.currentItem()
        if item is None:
            return
        self.model.deleteInstanceAt(item.row())

    #删除回调
    def deleteInstanceEvent(self,row:int):
        self.m_Table.removeRow(row)
        Utils.debugOut("delete position:",row)
        Utils.debugOut("delete after table rowCount:",self.m_Table.rowCount())
        self.adjustRowNo(row)
        Utils.debugOut("delete after current instance count:",self.model.getInstance().numInstances())


    #查找
    def search(self):
        searchStr,ok=QInputDialog.getText(self.m_Table,"Search...","输入查找的字符串")
        if ok:
            self.m_LastSearch=searchStr
            self.m_Table.setSearchString(searchStr)

    #清除查找记录
    def clearSearch(self):
        self.m_Table.setSearchString("")

    #插入新的实例
    def addInstance(self):
        index=self.m_Table.getSelectedRow()
        if index is None:
            index=self.model.getInstance().numInstances()
        self.model.insertInstance(index)

    #插入实例后回调函数
    def insertInstanceEvent(self,inst:Instances,row:int):
        self.m_Table.insertRow(row)
        self.m_Table.setItem(row,0,QTableWidgetItem(str(row+1)))
        self.m_Table.setRawItem(inst,row)
        self.adjustRowNo(row)
        Utils.debugOut("insert after current instance count:",self.model.getInstance().numInstances())

    #对实例数量产生影响时调用调整行数
    def adjustRowNo(self,begin:int,end:int=-1):
        if end == -1:
            end=self.model.getInstance().numInstances()
        for i in range(begin,end):
            self.m_Table.item(i,0).setText(str(i+1))

class ArffModel(QObject):
    delete_instance_signal=pyqtSignal(int)
    insert_instance_signal=pyqtSignal(Instances,int)
    def __init__(self,data:Instances=None):
        super().__init__()
        self.m_Data=data        #type:Instances
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

    #删除某个索引的实例
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

    def insertInstance(self,index:int):
        Utils.debugOut("insert instance position:",index)
        self.dialog=InserInstanceDialog()
        self.dialog.setAttributes(self.m_Data,index)
        self.dialog.submit_signal.connect(self.submitEvent)
        self.dialog.show()

    def submitEvent(self,inst:Instance,index:int):
        self.addUndoPoint()
        self.m_Data.add(inst,index)
        Utils.debugOut("insertDataList:",inst.m_Data)
        self.insert_instance_signal.emit(self.m_Data,index)
        # self.addUndoPoint()
        # vals=[]*self.m_Data.numAttributes()
        # for i in range(self.m_Data.numAttributes()):
        #     if self.m_Data.attribute(i).

