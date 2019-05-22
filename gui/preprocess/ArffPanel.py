import pickle
import tempfile
from typing import *

from core.Attributes import Attribute
from core.Instances import Instances, Instance
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from gui.common.SelectListDialog import SelectListDialog

from core.Utils import Utils
from gui.InsertInstanceDialog import InserInstanceDialog
from gui.TableWidget import TableWidget


class ArffPanel(QObject):
    state_changed_signal=pyqtSignal()
    def __init__(self,table:QTableWidget):
        super().__init__()
        self.m_Table=table      #type:TableWidget
        self.initalize()
        self.setTable()
        self.createMenu()
        self.attachMenuItemListener()
        self.m_Pass=False

    def initalize(self):
        #当前选中的列
        self.m_CurrentCol = -1
        self.m_LastSearch = ""
        self.m_Changed = False
        self.m_ChangeListeners = set()
        self.m_CurrentCombobox=None     #type:tuple
        self.model=ArffModel()

    def attachMenuItemListener(self):
        self.model.delete_instance_signal.connect(self.deleteInstanceEvent)
        self.model.insert_instance_signal.connect(self.insertInstanceEvent)
        self.model.update_instance_value_signal.connect(self.updateValueEvent)
        self.model.rename_attribute_signal.connect(self.renameEvent)
        self.model.delete_attribute_signal[int].connect(self.deleteAttributeEvent)
        self.model.delete_attribute_signal[list].connect(self.deleteAttributeEvent)
        self.model.undo_signal.connect(self.undoEvent)
        self.model.state_changed_signal.connect(self.stateChangedEvent)

    def setTable(self):
        self.m_Table.verticalHeader().setVisible(False)
        self.m_Table.horizontalHeader().setFixedHeight(40)
        # self.m_Table.setSelectionMode(QAbstractItemView.SingleSelection)
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
        self.replaceValuesMenuItem=self.headerMenu.addAction(u'Replace values with...')
        self.renameAttributeMenuItem=self.headerMenu.addAction(u'Rename attribute')
        self.deleteAttributeMenuItem=self.headerMenu.addAction(u'Delete attribute')
        self.deleteAttributesMenuItem=self.headerMenu.addAction(u'Delete attributes')
        self.optimalColumnWidthMenuItem=self.headerMenu.addAction(u'Optimal column width')

        self.tableMenu=QMenu()
        self.searchMenuItem=self.tableMenu.addAction(u'Search')
        self.clearSearchMenuItem=self.tableMenu.addAction(u'Clear search')
        self.deleteSelectedInstanceMenuItem=self.tableMenu.addAction(u'Delete selected instance')
        self.deleteAllSelectedInstancesMenuItem=self.tableMenu.addAction(u'Delete All selected instances')
        self.insertNewInstanceMenuItem=self.tableMenu.addAction(u'Insert new instance')


    def setMenu(self):
        isNull=self.model.getInstance() is None
        hasColumns=not isNull and self.model.getInstance().numAttributes()>0
        hasRows=not isNull and self.model.getInstance().numInstances()>0
        attSelected=hasColumns and self.model.isAttribute(self.m_CurrentCol)

        self.searchMenuItem.setEnabled(True)
        self.setAllValuesToMenuItem.setEnabled(attSelected)
        self.setMissingValuesToMenuItem.setEnabled(attSelected)
        self.replaceValuesMenuItem.setEnabled(attSelected)
        self.renameAttributeMenuItem.setEnabled(attSelected)
        self.deleteAttributeMenuItem.setEnabled(attSelected)
        self.deleteAttributesMenuItem.setEnabled(attSelected)
        self.deleteSelectedInstanceMenuItem.setEnabled(hasRows and self.m_Table.currentItem() is not None)
        self.deleteAllSelectedInstancesMenuItem.setEnabled(hasRows and len(self.m_Table.selectedIndexes())>0)

    def setInstances(self,inst:Instances):
        #封装数据实体
        self.model.setInstance(inst)
        #目前被选择的下拉框row,column
        self.m_CurrentCombobox=None     #tyep:tuple
        self.setModel(inst)
        self.model.clearUndo()
        self.m_Changed=False
        self.m_Table.itemChanged.connect(self.itemValueChanged)

    def itemValueChanged(self,item:QTableWidgetItem):
        if not self.m_Pass:
            row=item.row()
            column=item.column()
            print("row",row,"column",column)
            val=item.text()
            self.model.setValueAt(val,[row],column)
            print("val:",val)

    def getInstance(self):
        return self.model.getInstance()

    # def getStandardInstances(self):
    #     inst=self.model.getInstance()
    #     for i in range()

    def getSelectedRows(self)->List:
        res=set(index.row() for index in self.m_Table.selectedIndexes())
        res=sorted(res,reverse=True)
        return res

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
            item.setFlags(Qt.NoItemFlags)
            self.m_Table.setItem(row,0,item)
            self.m_Table.setRawItem(data,row)
            self.m_Table.setRowHeight(row,30)


    def selectedCombox(self,item:QTableWidgetItem):
        self.m_Pass=True
        if self.m_CurrentCombobox is not None:
            # newItem=QTableWidgetItem(self.m_Data.attribute(self.m_CurrentItem[1]-1).value(self.m_Data.instance(self.m_CurrentItem[0]).value(self.m_CurrentItem[1]-1)))
            widget=self.m_Table.cellWidget(self.m_CurrentCombobox.row(), self.m_CurrentCombobox.column())
            newItem=QTableWidgetItem(widget.currentText())
            if widget.currentText()=="":
                newItem.setBackground(QBrush(QColor(232,232,232)))
            elif widget.currentText()==self.m_LastSearch:
                newItem.setBackground(QBrush(Qt.red))
            self.m_Table.removeCellWidget(self.m_CurrentCombobox.row(), self.m_CurrentCombobox.column())
            self.m_Table.setItem(self.m_CurrentCombobox.row(), self.m_CurrentCombobox.column(), newItem)
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
            self.m_CurrentCombobox=item
            newItem.currentIndexChanged[str].connect(self.itemComboBoxChanged)
            newItem.showPopup()

        self.m_Pass = False

    def itemComboBoxChanged(self,text:str):
        if text == "":
            val=None
        else:
            val=text
        self.m_Table.removeCellWidget(self.m_CurrentCombobox.row(), self.m_CurrentCombobox.column())
        if text == "":
            val=None
        self.model.setValueAt(val,[self.m_CurrentCombobox.row()],self.m_CurrentCombobox.column())
        self.m_CurrentCombobox = None

    #表格菜单
    def generateMenu(self,pos):
        self.m_Table.setMenuClickNow(True)
        Utils.debugOut("currentSelectedRow:", self.m_Table.getSelectedRow())
        self.setMenu()
        action=self.tableMenu.exec_(self.m_Table.cursor().pos())
        if action == self.searchMenuItem:
            self.search()
        elif action == self.clearSearchMenuItem:
            self.clearSearch()
        elif action == self.deleteSelectedInstanceMenuItem:
            self.deleteInstance()
        elif action == self.insertNewInstanceMenuItem:
            self.addInstance()
        elif action == self.deleteAllSelectedInstancesMenuItem:
            self.deleteInstances()
        else:
            return
        self.m_Table.setMenuClickNow(False)

    #表头菜单
    def generateHeaderMenu(self,pos):
        self.m_Table.setMenuClickNow(True)
        self.m_CurrentCol=self.m_Table.horizontalHeader().logicalIndexAt(pos)
        Utils.debugOut("header menu item index:", self.m_Table.horizontalHeader().logicalIndexAt(pos))
        self.setMenu()
        action=self.headerMenu.exec_(self.m_Table.cursor().pos())
        if action == self.setAllValuesToMenuItem:
            self.setValues(self.setAllValuesToMenuItem)
        elif action == self.setMissingValuesToMenuItem:
            self.setValues(self.setMissingValuesToMenuItem)
        elif action == self.replaceValuesMenuItem:
            self.setValues(self.replaceValuesMenuItem)
        elif action == self.renameAttributeMenuItem:
            self.renameAttribute()
        elif action == self.deleteAttributeMenuItem:
            self.deleteAttribute()
        elif action == self.deleteAttributesMenuItem:
            self.deleteAttributes()
        elif action == self.optimalColumnWidthMenuItem:
            self.setOptimalColWidth()
        else:
            return
        self.m_Table.setMenuClickNow(False)


    #删除选中的实例
    def deleteInstance(self):
        item=self.m_Table.currentItem()
        if item is None:
            return
        self.model.deleteInstanceAt(item.row())

    def deleteInstances(self):
        indices=self.getSelectedRows()
        self.model.deleteInstances(indices)


    #删除回调
    def deleteInstanceEvent(self,row:int):
        self.m_Pass=True
        if self.m_CurrentCombobox is not None and self.m_CurrentCombobox.row() == row:
            self.m_CurrentCombobox=None
        self.m_Table.removeRow(row)
        Utils.debugOut("delete position:", row)
        Utils.debugOut("delete after table rowCount:", self.m_Table.rowCount())
        self.adjustRowNo(row)
        Utils.debugOut("delete after current instance count:", self.model.getInstance().numInstances())
        self.m_Pass=False


    def setSearchString(self,searchString:str):
        self.m_Pass=True
        self.m_Table.setSearchString(searchString)
        self.m_Pass=False

    #查找
    def search(self):
        searchStr,ok=QInputDialog.getText(self.m_Table,"Search...","输入查找的字符串")
        if ok:
            self.m_LastSearch=searchStr
            self.setSearchString(searchStr)

    #清除查找记录
    def clearSearch(self):
        self.setSearchString("")

    #插入新的实例
    def addInstance(self):
        self.m_Pass=True
        index=self.m_Table.getSelectedRow()
        if index is None:
            index=self.model.getInstance().numInstances()
        self.model.insertInstance(index)
        self.m_Pass=False

    #插入实例后回调函数
    def insertInstanceEvent(self,inst:Instances,row:int):
        self.m_Pass=True
        self.m_Table.insertRow(row)
        self.m_Table.setItem(row,0,QTableWidgetItem(str(row+1)))
        self.m_Table.setRawItem(inst,row)
        self.adjustRowNo(row)
        Utils.debugOut("insert after current instance count:", self.model.getInstance().numInstances())
        self.m_Pass=False

    #对实例数量产生影响时调用调整行数
    def adjustRowNo(self,begin:int,end:int=-1):
        if end == -1:
            end=self.model.getInstance().numInstances()
        for i in range(begin,end):
            self.m_Table.item(i,0).setText(str(i+1))

    #修改实例值
    def setValues(self,menuItem:QAction):
        if menuItem == self.setAllValuesToMenuItem:
            title="Set all values..."
            msg="New value for all values"
        elif menuItem == self.setMissingValuesToMenuItem:
            title = "Replace missing values..."
            msg = "New value for MISSING values"
        elif menuItem == self.replaceValuesMenuItem:
            title = "Replace values..."
            msg = "Old value"
        else:
            return
        value,ok=QInputDialog.getText(self.m_Table,title,msg)
        if ok:
            if menuItem == self.replaceValuesMenuItem:
                valueNew,okAgain=QInputDialog.getText(self.m_Table,title,"New value")
                if not okAgain:
                    return
                if valueNew == "" or valueNew.lower() == "nan" or valueNew.lower() == "none":
                    valueNew=None
            updateIndexList=[]
            if value == "" or value.lower() == "nan" or value.lower() == 'none':
                value = None
            for i in range(self.m_Table.rowCount()):
                if menuItem == self.setAllValuesToMenuItem:
                    if value != self.model.getInstance().instance(i).value(self.m_CurrentCol-1):
                        # self.model.setValueAt(value,i,self.m_CurrentCol)
                        updateIndexList.append(i)
                elif menuItem == self.setMissingValuesToMenuItem and self.model.isMissingAt(i,self.m_CurrentCol) and value is not None:
                    # self.model.setValueAt(value,i,self.m_CurrentCol)
                    updateIndexList.append(i)
                elif menuItem == self.replaceValuesMenuItem  and self.model.getValueAt(i,self.m_CurrentCol) is not None\
                    and str(self.model.getValueAt(i,self.m_CurrentCol)) == value:
                    # self.model.setValueAt(valueNew,i,self.m_CurrentCol)
                    updateIndexList.append(i)
            if menuItem == self.replaceValuesMenuItem:
                self.model.setValueAt(valueNew,updateIndexList,self.m_CurrentCol)
            else:
                self.model.setValueAt(value,updateIndexList,self.m_CurrentCol)

    def updateValueEvent(self,rowIndexList:List[int],columnIndex:int,newValue):
        self.m_Pass=True
        for i in rowIndexList:
            item=self.m_Table.item(i,columnIndex)
            item.setText(newValue)
            if newValue is None:
                item.setBackground(QBrush(QColor(232,232,232)))
            elif newValue == self.m_LastSearch:
                item.setBackground(QBrush(Qt.red))
        self.m_Pass=False

    #重命名
    def renameAttribute(self):
        if self.model.getAttributeAt(self.m_CurrentCol) is None:
            return
        newName,ok=QInputDialog.getText(self.m_Table,"Rename attribute...","Enter new Attribute name",text=self.model.getAttributeAt(self.m_CurrentCol).name())
        if ok:
            if newName == "":
                return
            self.model.renameAttributeAt(self.m_CurrentCol,newName)

    def renameEvent(self,columnIndex:int,newName:str):
        lab = str(columnIndex) + ":"
        lab += newName + '\n'
        lab += Attribute.typeToString(self.model.getInstance().attribute(columnIndex-1).type()).capitalize()
        self.m_Table.setHorizontalHeaderItem(columnIndex,QTableWidgetItem(lab))
        self.m_Table.horizontalHeader().resizeSection(columnIndex,self.m_Table.horizontalHeader().sectionSizeFromContents(columnIndex).width())

    #删除列(属性)
    def deleteAttribute(self):
        if self.model.getInstance().classIndex() == self.m_CurrentCol-1:
            QMessageBox.warning(self.m_Table,"Warning","无法删除作为类基准的属性",QMessageBox.Yes,QMessageBox.Yes)
            return
        reply=QMessageBox.question(self.m_Table,"Confirm...","确认删除 "+self.model.getAttributeAt(self.m_CurrentCol).name()+" 属性？",QMessageBox.Yes | QMessageBox.No,QMessageBox.No)
        if reply == QMessageBox.No:
            return
        self.model.deleteAttributeAt(self.m_CurrentCol)

    #删除多个属性
    def deleteAttributes(self):
        dialog=SelectListDialog(self.m_Table)
        li=[]
        for i in range(self.model.getInstance().numAttributes()):
            li.append(self.model.getInstance().attribute(i).name())
        dialog.setList(li)
        dialog.show()
        dialog.select_attributes_signal.connect(self.sureToDelete)

    def sureToDelete(self,attrs:List):
        reply = QMessageBox.question(self.m_Table, "Confirm...","确认删除所选的 " + str(len(attrs)) + " 个属性？",QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            indices=[]
            for index in attrs:
                indices.append(index+1-len(indices))
            self.model.deleteAttributes(indices)

    def deleteAttributeEvent(self, columnIndex):
        if isinstance(columnIndex,int):
            if self.m_CurrentCombobox is not None and self.m_CurrentCombobox.column() == columnIndex:
                self.m_CurrentCombobox=None
            self.m_Table.removeColumn(columnIndex)
        elif isinstance(columnIndex,list):
            for i in columnIndex:
                if self.m_CurrentCombobox is not None and self.m_CurrentCombobox.column() == i:
                    self.m_CurrentCombobox = None
                self.m_Table.removeColumn(i)
        headerLabels = ["No."]
        for column in range(self.model.getInstance().numAttributes()):
            lab = str(column + 1) + ":"
            lab += self.model.getInstance().attribute(column).name() + '\n'
            lab += Attribute.typeToString(self.model.getInstance().attribute(column).type()).capitalize()
            headerLabels.append(lab)
        self.m_Table.setHorizontalHeaderLabels(headerLabels)

    #调整列宽自适应内容宽度
    def setOptimalColWidth(self):
        self.m_Table.horizontalHeader().resizeSection(self.m_CurrentCol,self.m_Table.horizontalHeader().
                                                      sectionSizeFromContents(self.m_CurrentCol).width())

    def canUndo(self):
        return self.model.canUndo()

    def undo(self):
        if self.canUndo():
            self.model.undo()

    def undoEvent(self,inst:Instances):
        self.m_Pass=True
        if self.m_CurrentCombobox is not None:
            # newItem=QTableWidgetItem(self.m_Data.attribute(self.m_CurrentItem[1]-1).value(self.m_Data.instance(self.m_CurrentItem[0]).value(self.m_CurrentItem[1]-1)))
            widget=self.m_Table.cellWidget(self.m_CurrentCombobox.row(), self.m_CurrentCombobox.column())
            newItem=QTableWidgetItem(widget.currentText())
            if widget.currentText()=="":
                newItem.setBackground(QBrush(QColor(232,232,232)))
            elif widget.currentText()==self.m_LastSearch:
                newItem.setBackground(QBrush(Qt.red))
            self.m_Table.removeCellWidget(self.m_CurrentCombobox.row(), self.m_CurrentCombobox.column())
            self.m_Table.setItem(self.m_CurrentCombobox.row(), self.m_CurrentCombobox.column(), newItem)
            self.m_CurrentCombobox=None
        self.setModel(inst)
        self.m_Pass=False

    def stateChangedEvent(self):
        self.state_changed_signal.emit()


class ArffModel(QObject):
    delete_instance_signal=pyqtSignal(int)
    insert_instance_signal=pyqtSignal(Instances,int)
    update_instance_value_signal=pyqtSignal(list,int,object)
    rename_attribute_signal=pyqtSignal(int,str)
    delete_attribute_signal=pyqtSignal([int],[list])
    undo_signal=pyqtSignal(Instances)
    state_changed_signal=pyqtSignal()

    def __init__(self,data:Instances=None):
        super().__init__()
        self.m_Data=data        #type:Instances
        self.m_UndoList=[]      #type:List
        self.m_Cache=dict()
        self.m_IgnoreChanges=False

    def setInstance(self,data:Instances):
        self.m_Data=data
        self.m_Cache.clear()

    def clearUndo(self):
        self.m_UndoList.clear()

    def getInstance(self):
        return self.m_Data

    def isAttribute(self,columnIndex:int):
        return columnIndex>0 and columnIndex<self.m_Data.numAttributes()+1

    def getAttributeAt(self,columnIndex:int)->Attribute:
        if self.isAttribute(columnIndex):
            return self.m_Data.attribute(columnIndex-1)

    #删除某个索引的实例
    def deleteInstanceAt(self,rowIndex:int):
        if rowIndex<self.m_Data.numInstances():
            if not self.m_IgnoreChanges:
                self.addUndoPoint()
            self.m_Data.delete(rowIndex)
            self.delete_instance_signal.emit(rowIndex)

    def deleteInstances(self,rowIndices:list):
        self.addUndoPoint()
        self.m_IgnoreChanges=True
        for row in rowIndices:
            self.deleteInstanceAt(row)
        self.m_IgnoreChanges=False


    def addUndoPoint(self):
        if self.m_Data is not None:
            temp=tempfile.TemporaryFile()
            pickle.dump(self.m_Data,temp)
            temp.seek(0)
            self.m_UndoList.append(temp)
            self.state_changed_signal.emit()
        Utils.debugOut("Now undo list len:", len(self.m_UndoList))

    def insertInstance(self,index:int):
        Utils.debugOut("insert instance position:", index)
        self.dialog=InserInstanceDialog()
        self.dialog.setAttributes(self.m_Data,index)
        self.dialog.submit_signal.connect(self.submitEvent)
        self.dialog.show()

    def submitEvent(self,inst:Instance,index:int):
        self.addUndoPoint()
        self.m_Data.add(inst,index)
        Utils.debugOut("insertDataList:", inst.m_AttValues)
        self.insert_instance_signal.emit(self.m_Data,index)

    def setValueAt(self,value,rowIndexList:List,columnIndex:int):
        self.addUndoPoint()
        for rowIndex in rowIndexList:
            type=self.getType(columnIndex)
            index=columnIndex-1
            inst=self.m_Data.instance(rowIndex)
            att=inst.attribute(index)

            if value is None:
                inst.setValue(index, Utils.missingValue())
            else:
                if type == Attribute.NUMERIC:
                    inst.setValue(index,float(value))
                elif type == Attribute.NOMINAL:
                    if att.indexOfValue(value) > -1:
                        inst.setValue(index,att.indexOfValue(value))
                        # print(att.indexOfValue(value))
                    else:
                        rowIndexList=[]
                        break
                elif type == Attribute.STRING:
                    inst.setValue(index,value)
                elif type == Attribute.DATE:
                    #TODO
                    pass
        self.update_instance_value_signal.emit(rowIndexList,columnIndex,value)


    def getRowCount(self):
        return self.m_Data.numInstances()

    def getColumnCount(self):
        return self.m_Data.numAttributes()+1

    def isMissingAt(self,rowIndex:int,columnIndex:int):
        res=False
        if rowIndex>=0 and rowIndex<self.getRowCount() and self.isAttribute(columnIndex):
            res=self.m_Data.instance(rowIndex).isMissing(columnIndex-1)
        return res

    def getType(self,columnIndex:int):
        res=Attribute.STRING
        if self.isAttribute(columnIndex):
            res=self.m_Data.attribute(columnIndex-1).type()
        return res

    def getValueAt(self,rowIndex:int,columnIndex:int):
        key=str(rowIndex)+'-'+str(columnIndex)
        res=None
        if rowIndex>=0 and rowIndex<self.getRowCount() and columnIndex>=0 and columnIndex<self.getColumnCount():
            if columnIndex == 0:
                return rowIndex+1
            else:
                if self.isMissingAt(rowIndex,columnIndex):
                    res=None
                else:
                    if key in self.m_Cache:
                        res=self.m_Cache.get(key)
                    else:
                        attrType=self.getType(columnIndex)
                        if attrType == Attribute.NUMERIC:
                            res=self.m_Data.instance(rowIndex).value(columnIndex-1)
                        else:
                            res=self.m_Data.instance(rowIndex).stringValue(columnIndex-1)
                        self.m_Cache.update({key:res})
        return res

    def renameAttributeAt(self,columnIndex:int,newName:str):
        if self.isAttribute(columnIndex):
            self.addUndoPoint()
            res=self.m_Data.renameAttribute(columnIndex-1,newName)
            if res:
                self.rename_attribute_signal.emit(columnIndex,newName)

    def deleteAttributeAt(self,columnIndex:int):
        if self.isAttribute(columnIndex):
            self.addUndoPoint()
            self.m_Data.deleteAttributeAt(columnIndex-1)
            self.delete_attribute_signal[int].emit(columnIndex)

    def deleteAttributes(self,indexList:List):
        self.addUndoPoint()
        Utils.debugOut('will delete attributes index:', indexList)
        for i in indexList:
            self.m_Data.deleteAttributeAt(i-1)
        self.delete_attribute_signal[list].emit(indexList)

    def canUndo(self):
        return len(self.m_UndoList)>0

    def undo(self):
        if self.canUndo():
            tempFile=self.m_UndoList[-1]
            self.m_UndoList.pop()
            data=pickle.load(tempFile)
            tempFile.close()
            self.setInstance(data)
            self.undo_signal.emit(self.m_Data)
            self.state_changed_signal.emit()

