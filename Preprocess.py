# from CallMain import MainWindow
import os
from copy import *

import arff
from gui.preprocess.InstanceSummaryPanel import InstanceSummaryPanel
from core.Instances import Instances
from gui.PropertyPanel import PropertyPanel
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from core.Thread import Thread
from gui.ViewerDialog import ViewerDialog
from gui.common.GenericObjectEditor import GenericObjectEditor

from core.Utils import Utils
from filters.Filter import Filter
from filters.attribute.Remove import Remove
from gui.preprocess.AttributeSelectionPanel import AttributeSelectionPanel
from gui.preprocess.AttributeSummaryPanel import AttributeSummaryPanel
from gui.preprocess.AttributeVisualizationPanel import AttributeVisualizationPanel


class PreprocessPanel(QObject):
    def __init__(self,win:'MainWindow',parent=None):
        super().__init__(parent)
        # self.m_FilterEditor=GenericObjectEditor()
        # self.m_FilterEditor
        self.instanceSummaryPanel=InstanceSummaryPanel(win)
        self.m_AttPanel=AttributeSelectionPanel(win)
        self.m_AttSummaryPanel=AttributeSummaryPanel(win)
        self.m_AttVisualizePanel=AttributeVisualizationPanel(win)
        self.m_Instances=None     #type:Instances
        self.m_Explor=win
        self.m_openBut=win.open_btn
        self.m_editBut=win.edit_btn
        self.m_tab=win.tab
        self.m_tabWidget=win.tabWidget      #type:QTabWidget
        self.m_ApplyBut=win.apply_btn       #type:QPushButton
        self.m_StopBut=win.filter_stop_btn      #type:QPushButton
        self.m_SaveBut=win.save_btn
        self.m_Option=win.option_filter
        self.m_ChooseBut=win.chose_btn
        self.m_RemoveButton=win.remove_btn
        self.m_FileName=""
        self.m_RunThread=None       #type:Thread
        self.m_FilterEditor=GenericObjectEditor()
        self.m_FilterPanel=PropertyPanel(self,self.m_FilterEditor)
        self.m_FilterEditor.setClassType(Filter)

        self.initSetting()
        self.attachListener()

    def propertyChanged(self,value:str):
        self.m_ApplyBut.setEnabled(self.getInstances() is not None)

    def openFile(self):
        filename = QFileDialog.getOpenFileName(self.m_tab, '打开文件', '/', 'Arff data files(*.arff);;CSV data files(*.csv)')
        file = open(filename[0], 'rb')
        self.m_FileName=os.path.basename(file.name).split('.')[0]
        # 解析arff
        with file:
            s = file.read().decode('utf-8')
        try:
            data = arff.loads(s)
        except arff.BadLayout:
            Utils.DiglogWarning(self.m_Explor, "Syntax Errors in Data Sets")
            return
        inst = Instances(data)
        print(data)
        self.setInstances(inst)

        self.m_tabWidget.setTabEnabled(1, True)
        self.m_tabWidget.setTabEnabled(2, True)

    def saveFile(self):
        filename=QFileDialog.getSaveFileName(self.m_tab,'保存文件','/'+self.m_FileName,'Arff data files(*.arff)')
        with open(filename[0],'w') as f:
            text=self.m_Instances.toArffString()
            f.write(text)

    def getOptionBut(self):
        return self.m_Option

    def getChooseBut(self):
        return self.m_ChooseBut

    def setInstances(self,inst:Instances):
        self.m_Instances=inst
        # 数据集信息面板
        self.instanceSummaryPanel.setInstance(self.m_Instances)
        # 属性面板
        self.m_AttPanel.setInstance(self.m_Instances)
        # 属性详情面板
        self.m_AttSummaryPanel.setInstance(self.m_Instances)
        # 下拉框
        self.m_AttVisualizePanel.setInstance(self.m_Instances)

        # UI初始化
        self.m_AttSummaryPanel.setAttribute(0)
        self.m_AttVisualizePanel.setAttribute(0)

        self.m_ApplyBut.setEnabled(True)
        self.m_SaveBut.setEnabled(True)
        self.m_editBut.setEnabled(True)

    # def mousePressEvent(self, a0:QMouseEvent):
    #     if a0.button()==Qt.LeftButton:
    #         self.setFocus()

    def initSetting(self):
        #禁用控件
        self.m_editBut.setEnabled(False)
        self.m_SaveBut.setEnabled(False)
        self.m_ApplyBut.setEnabled(False)
        self.m_StopBut.setEnabled(False)
        self.m_tabWidget.setTabEnabled(1, False)
        self.m_tabWidget.setTabEnabled(2, False)


    def attachListener(self):
        self.m_openBut.clicked.connect(self.openFile)
        self.m_SaveBut.clicked.connect(self.saveFile)
        self.m_AttPanel.m_TableModel.m_Table.cellClicked.connect(self.tableCellClick)
        self.m_editBut.clicked.connect(self.edit)
        # self.m_tabWidget.currentChanged.connect(self.tabChangedListener)
        self.m_Explor.tab_changed_signal.connect(self.tabChangedListener)
        self.m_RemoveButton.clicked.connect(self.removeClicked)
        self.m_FilterEditor.classifier_changed.connect(self.propertyChanged)
        self.m_ApplyBut.clicked.connect(self.applyButClicked)

    def applyButClicked(self):
        self.applyFilter(self.m_FilterEditor.getValue())

    def tabChangedListener(self,panel:QObject):
        panel.setInstances(self.m_Instances)

    def tableCellClick(self,row,column):
        self.m_AttSummaryPanel.setAttribute(row)
        self.m_AttVisualizePanel.setAttribute(row)

    def edit(self):
        classIndex=self.m_AttVisualizePanel.getColoringIndex()
        cpInstance=deepcopy(self.m_Instances)
        cpInstance.setClassIndex(classIndex)
        self.dialog=ViewerDialog()
        self.dialog.resize(1000,600)
        self.dialog.setInstances(cpInstance)
        self.dialog.show()
        self.dialog.close_signal.connect(self.viewTableCloseEvent)

    def viewTableCloseEvent(self,inst:Instances):
        if self.m_Instances.classIndex()<0:
            inst.setClassIndex(-1)
        Utils.debugOut("\n\nnewInstance numAttribute:", inst.numAttributes())
        self.setInstances(inst)


    def removeClicked(self):
        r=Remove()
        selected=self.m_AttPanel.m_TableModel.getSelectedAttributes()
        if len(selected) == 0:
            return
        if len(selected) == self.m_Instances.numAttributes():
            Utils.DiglogWarning(self.m_Explore, "Can't remove all attributes from data!\n")
            return
        r.setAttributeIndicesArray(selected)
        self.applyFilter(r)

    def applyFilter(self,filter:Filter):
        if self.m_RunThread is None:
            self.m_RunThread=Thread(target=self.threadRun,args=(filter,))
            self.m_RunThread.setPriority(QThread.LowPriority)
            self.m_RunThread.start()


    def threadRun(self,filter:Filter):
        if filter is not None:
            #addUndo
            classIndex=self.m_AttVisualizePanel.getColoringIndex()
            cp=Instances(self.m_Instances)
            cp.setClassIndex(classIndex)
            self.m_StopBut.setEnabled(True)
            filterCopy=deepcopy(filter)
            filterCopy.setInputFormat(cp)
            newInstances=Filter.useFilter(cp,filterCopy)
            self.m_StopBut.setEnabled(False)
            if newInstances is None or newInstances.numAttributes() < 1:
                raise Exception("Dataset is empty.")
            #addUndo
            self.m_AttVisualizePanel.setColoringIndex(cp.classIndex())
            if self.m_Instances.classIndex() < 0:
                newInstances.setClassIndex(-1)
            self.m_Instances=newInstances
            self.setInstances(self.m_Instances)
            self.m_RunThread=None

    def getInstances(self):
        return self.m_Instances