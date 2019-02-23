import arff
from AttributeSummaryPanel import AttributeSummaryPanel
from AttributeVisualizationPanel import AttributeVisualizationPanel
from InstanceSummaryPanel import InstanceSummaryPanel
from Instances import *
from PyQt5.QtWidgets import *
from ViewerDialog import ViewerDialog
from gui.preprocess.AttributeSelectionPanel import AttributeSelectionPanel


class PreprocessPanel():
    def __init__(self,win:'MainWindow'):
        # self.m_FilterEditor=GenericObjectEditor()
        # self.m_FilterEditor
        self.instanceSummaryPanel=InstanceSummaryPanel(win)
        self.attributePanel=AttributeSelectionPanel(win)
        self.attributeSummaryPanel=AttributeSummaryPanel(win)
        self.attributeVisualizationPanel=AttributeVisualizationPanel(win)
        self.m_Instances=None     #type:Instances
        self.m_Explor=win
        self.m_openBut=win.open_btn
        self.m_editBut=win.edit_btn
        self.m_tab=win.tab
        self.m_tabWidget=win.tabWidget      #type:QTabWidget
        self.m_applyBut=win.apply_btn
        self.m_saveBut=win.save_btn

        self.initSetting()
        self.attachListener()



    def openFile(self):
        filename = QFileDialog.getOpenFileName(self.m_tab, '选择文件', '/', 'Arff data files(*.arff);;CSV data files(*.csv)')
        file = open(filename[0], 'rb')
        # 解析arff
        with file:
            s = file.read().decode('utf-8')
        data = arff.loads(s)
        print(data)
        inst = Instances(data)
        self.setInstances(inst)

        self.m_tabWidget.setTabEnabled(1, True)
        self.m_tabWidget.setTabEnabled(2, True)


    def setInstances(self,inst:Instances):
        self.m_Instances=inst
        # 数据集信息面板
        self.instanceSummaryPanel.setInstance(self.m_Instances)
        # 属性面板
        self.attributePanel.setInstance(self.m_Instances)
        # 属性详情面板
        self.attributeSummaryPanel.setInstance(self.m_Instances)
        # 下拉框
        self.attributeVisualizationPanel.setInstance(self.m_Instances)

        # UI初始化
        self.attributeSummaryPanel.setAttribute(0)
        self.attributeVisualizationPanel.setAttribute(0)

        self.m_applyBut.setEnabled(True)
        self.m_saveBut.setEnabled(True)
        self.m_editBut.setEnabled(True)

    # def mousePressEvent(self, a0:QMouseEvent):
    #     if a0.button()==Qt.LeftButton:
    #         self.setFocus()

    def initSetting(self):
        #禁用控件
        self.m_editBut.setEnabled(False)
        self.m_saveBut.setEnabled(False)
        self.m_applyBut.setEnabled(False)
        self.m_tabWidget.setTabEnabled(1, False)
        self.m_tabWidget.setTabEnabled(2, False)


    def attachListener(self):
        self.m_openBut.clicked.connect(self.openFile)
        self.attributePanel.m_TableModel.m_Table.cellClicked.connect(self.tableCellClick)
        self.m_editBut.clicked.connect(self.edit)
        self.m_tabWidget.currentChanged.connect(self.tabChangedListener)

    def tabChangedListener(self,index:int):
        self.m_Explor.getClassiferPanel().setInstances(self.m_Instances)

    def tableCellClick(self,row,column):
        self.attributeSummaryPanel.setAttribute(row)
        self.attributeVisualizationPanel.setAttribute(row)

    def edit(self):
        classIndex=self.attributeVisualizationPanel.getColoringIndex()
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
        Utils.debugOut("\n\nnewInstance numAttribute:",inst.numAttributes())
        self.setInstances(inst)
