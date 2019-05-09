
from typing import *

from core.Attributes import Attribute
from core.Instances import Instances
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from core.Utils import Utils
from core.AttributeStats import AttributeStats
from gui.designUI.Main import Ui_MainWindow


#TODO
class AttributeSummaryPanel():
    NO_SOURCE="None"
    def __init__(self,ui:Ui_MainWindow):
        self.m_AttributeNameLab=ui.select_attr_name
        self.m_AttributeWeightLab=ui.select_attr_weight
        self.m_WeightLab=ui.select_attr_weight_lab
        self.m_AttributeTypeLab=ui.select_attr_type
        self.m_MissingLab=ui.select_attr_missing
        self.m_UniqueLab=ui.select_attr_unique
        self.m_DistinctLab=ui.select_attr_distinct
        self.m_StatsTable=ui.selected_table
        self.m_AttributeStats=None  #type:list[AttributeStats]
        self.initalize()

    def initalize(self):
        self.m_StatsTable.verticalHeader().setVisible(False)
        self.m_StatsTable.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.m_StatsTable.horizontalHeader().setStretchLastSection(True)
        self.m_StatsTable.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.m_StatsTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.m_StatsTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.m_StatsTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.m_StatsTable.setShowGrid(False)

    def setInstance(self,inst:Instances):
        self.m_Instance=inst
        self.m_AttributeStats=[None]*inst.numAttributes()
        self.m_AttributeNameLab.setText(self.NO_SOURCE)
        self.m_AttributeTypeLab.setText(self.NO_SOURCE)
        self.m_AttributeWeightLab.setText(self.NO_SOURCE)
        self.m_MissingLab.setText(self.NO_SOURCE)
        self.m_UniqueLab.setText(self.NO_SOURCE)
        self.m_DistinctLab.setText(self.NO_SOURCE)


    def setAttribute(self,index:int):
        self.setHeader(index)
        if self.m_AttributeStats[index] is None:
            self.m_AttributeStats[index]=self.m_Instance.attributeStats(index)
        else:
            self.setDerived(index)


    def setHeader(self,index:int):
        attr=self.m_Instance.attribute(index)
        attrType=attr.type()
        self.m_AttributeNameLab.setText(attr.name())
        if attrType == Attribute.NUMERIC:
            self.m_AttributeTypeLab.setText("Numeric")
        elif attrType == Attribute.NOMINAL:
            self.m_AttributeTypeLab.setText("Nominal")
        elif attrType == Attribute.DATE:
            self.m_AttributeTypeLab.setText("Date")
        elif attrType == Attribute.STRING:
            self.m_AttributeTypeLab.setText("String")
        else:
            self.m_AttributeTypeLab.setText("Unknown")

        #目前只考虑权重为1的情况
        self.m_AttributeWeightLab.setVisible(False)
        self.m_WeightLab.setVisible(False)

        self.m_MissingLab.setText("...")
        self.m_DistinctLab.setText("...")
        self.m_UniqueLab.setText("...")

    def setDerived(self,index:int):
        attrStats=self.m_AttributeStats[index]
        percent=round(100.0*attrStats.missingCount/attrStats.totalCount)
        self.m_MissingLab.setText(str(attrStats.missingCount)+" ("+str(percent)+"%)")
        percent=round(100.0*attrStats.uniqueCount/attrStats.totalCount)
        self.m_UniqueLab.setText(str(attrStats.uniqueCount)+" ("+str(percent)+"%)")
        self.m_DistinctLab.setText(str(attrStats.distinctCount))
        self.setTable(attrStats,index)


    def setTable(self,attrStats:AttributeStats,index:int):
        if attrStats.nominalCounts is not None:
            att=self.m_Instance.attribute(index)
            colNames=["No.","Label","Count","Weight"]
            data=[]
            for i in range(len(attrStats.nominalCounts)):
                val=[]
                item_No=QTableWidgetItem(str(i+1))
                item_No.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                val.append(item_No)
                val.append(QTableWidgetItem(att.value(i)))
                val.append(QTableWidgetItem(str(int(attrStats.nominalCounts[i]))))
                val.append(QTableWidgetItem(Utils.doubleToString(attrStats.nominalWeights[i], 3)))
                data.append(val)
            #更新表头，填数据
            self.fillData(data,colNames)
            self.m_StatsTable.horizontalHeader().resizeSection(0,60)
        elif attrStats.numericStats is not None:
            colNames=["Statistic","Value"]
            data=[]
            val=[QTableWidgetItem("Minimum")]
            val.append(QTableWidgetItem(Utils.doubleToString(attrStats.numericStats.min, 3)))
            data.append(val)
            val=[QTableWidgetItem("Maximum")]
            val.append(QTableWidgetItem(Utils.doubleToString(attrStats.numericStats.max, 3)))
            data.append(val)
            val=[QTableWidgetItem("Mean")]
            val.append(QTableWidgetItem(Utils.doubleToString(attrStats.numericStats.mean, 3)))
            data.append(val)
            val=[QTableWidgetItem("StdDev")]
            val.append(QTableWidgetItem(Utils.doubleToString(attrStats.numericStats.stdDev, 3)))
            data.append(val)
            self.fillData(data,colNames)
            self.m_StatsTable.horizontalHeader().resizeSection(0,self.m_StatsTable.width()/2)



    def fillData(self,data:List[List[QTableWidgetItem]],labNames:List[str]):
        self.m_StatsTable.setColumnCount(len(labNames))
        self.m_StatsTable.setRowCount(len(data))
        self.m_StatsTable.setHorizontalHeaderLabels(labNames)
        for row in range(len(data)):
            self.m_StatsTable.setRowHeight(row,25)
            for column in range(len(data[row])):
                self.m_StatsTable.setItem(row,column,data[row][column])


    # def setDefault(self):

