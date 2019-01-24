
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Main import Ui_MainWindow
from Instances import Instances
from typing import *


class AttributeSelectionPanel():

    first=False
    class AttributeTableModel():
        def __init__(self,table:QTableWidget):
            self.m_Table=table

        def setInstance(self,inst:Instances):
            self.m_Instance=inst
            self.m_Selected=[False]*inst.numAttributes()
            self.m_Table.setCurrentCell(0,0)
            self.setTable()

        # 获取Table中每条的信息,1:编号  2:勾选状态 3:属性名
        def getValueAt(self, row: int, column: int):
            if column == 0:
                return row + 1
            elif column == 1:
                return self.m_Selected[row]
            elif column == 2:
                return self.m_Instance.attribute(row).name()
            else:
                return None

        # 设置属性的勾选状态
        def setValueAt(self, row: int, column: int):
            if column == 1:
                self.m_Selected[row] = bool(self.m_Table.item(row, column).checkState())

        # 返回属性条目数量
        def getRowCount(self):
            return len(self.m_Selected)

        def getColumnCount(self):
            return 3

        # 返回勾选的属性数量
        def getSelectedAttributes(self)->List[int]:
            res = []
            for i in range(self.getRowCount()):
                if self.m_Selected[i] is True:
                    res.append(i)
            return res

        def setTable(self):
            if self.m_Instance is not None:
                colNames = ["No.", " ", "Name"]
                data = []
                for i in range(self.m_Instance.numAttributes()):
                    val = []
                    item_No = QTableWidgetItem(str(i + 1))
                    item_No.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    val.append(item_No)
                    item_Check = QTableWidgetItem()
                    item_Check.setCheckState(Qt.Unchecked)
                    val.append(item_Check)
                    val.append(QTableWidgetItem(self.m_Instance.attribute(i).name()))
                    data.append(val)
                # 更新表头，填数据
                self.fillData(data, colNames)
                self.m_Table.horizontalHeader().resizeSection(0, 100)
                self.m_Table.horizontalHeader().resizeSection(1, 20)

        def fillData(self, data: List[List[QTableWidgetItem]], labNames: List[str]):
            self.m_Table.setColumnCount(len(labNames))
            self.m_Table.setRowCount(len(data))
            self.m_Table.setHorizontalHeaderLabels(labNames)
            for row in range(len(data)):
                for column in range(len(data[row])):
                    self.m_Table.setItem(row, column, data[row][column])

    def __init__(self,ui:Ui_MainWindow):
        self.m_IncludeAll=ui.all_btn
        self.m_Invert=ui.invert_btn
        self.m_None=ui.none_btn
        self.m_RemoveAll=ui.remove_btn
        self.m_TableModel=self.AttributeTableModel(ui.attr_table)

        self.m_IncludeAll.setEnabled(False)
        self.m_Invert.setEnabled(False)
        self.m_None.setEnabled(False)
        self.m_RemoveAll.setEnabled(False)


    #绑定dataSet
    def setInstance(self,inst:Instances):
        self.m_Instance=inst
        self.m_TableModel.setInstance(inst)
        self.m_IncludeAll.setEnabled(True)
        self.m_Invert.setEnabled(True)
        self.m_None.setEnabled(True)
        self.m_RemoveAll.setEnabled(False)

        if not self.first:
            self.m_TableModel.m_Table.cellChanged.connect(self.tableChanged)
            self.m_Invert.clicked.connect(self.invertBtnClick)
            self.m_None.clicked.connect(self.noneBtnClick)
            self.m_IncludeAll.clicked.connect(self.allBtnClick)
            self.first=True



    #checkBox 状态监听
    def tableChanged(self,row,column):
        self.m_TableModel.setValueAt(row, column)
        if len(self.m_TableModel.getSelectedAttributes()) > 0:
            self.m_RemoveAll.setEnabled(True)
        else:
            self.m_RemoveAll.setEnabled(False)

    def allBtnClick(self):
        len = self.m_TableModel.getRowCount()
        for i in range(len):
            self.m_TableModel.m_Table.item(i, 1).setCheckState(Qt.Checked)

    def noneBtnClick(self):
        len = self.m_TableModel.getRowCount()
        for i in range(len):
            self.m_TableModel.m_Table.item(i, 1).setCheckState(Qt.Unchecked)

    def invertBtnClick(self):
        len = self.m_TableModel.getRowCount()
        for i in range(len):
            state = self.m_TableModel.m_Table.item(i, 1).checkState()
            self.m_TableModel.m_Table.item(i, 1).setCheckState(state ^ Qt.Checked)

