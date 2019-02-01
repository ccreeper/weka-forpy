from InstanceSummaryPanel import InstanceSummaryPanel
from AttributeSelectionPanel import AttributeSelectionPanel
from AttributeSummaryPanel import AttributeSummaryPanel
from AttributeVisualizationPanel import AttributeVisualizationPanel
from ViewerDialog import ViewerDialog
import cgitb
import arff
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Instances import *
from Main import *


class PreprocessPanel(QMainWindow,Ui_MainWindow):
    def __init__(self,parent=None):
        super().__init__(parent)
        super().setupUi(self)
        # self.m_FilterEditor=GenericObjectEditor()
        # self.m_FilterEditor
        self.initSetting()
        self.instanceSummaryPanel=InstanceSummaryPanel(self)
        self.attributePanel=AttributeSelectionPanel(self)
        self.attributeSummaryPanel=AttributeSummaryPanel(self)
        self.attributeVisualizationPanel=AttributeVisualizationPanel(self)
        self.attachListener()

    def openFile(self):
        filename = QFileDialog.getOpenFileName(self.tab, '选择文件', '/', 'Arff data files(*.arff);;CSV data files(*.csv)')
        file = open(filename[0], 'rb')
        # 解析arff
        with file:
            s = file.read().decode('utf-8')
        data = arff.loads(s)
        print(data)
        self.m_Instances = Instances(data)
        self.setInstances(self.m_Instances)

        self.tabWidget.setTabEnabled(1, True)
        self.tabWidget.setTabEnabled(2, True)


    def setInstances(self,inst:Instances):
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

        self.apply_btn.setEnabled(True)
        self.save_btn.setEnabled(True)
        self.edit_btn.setEnabled(True)

    def mousePressEvent(self, a0:QMouseEvent):
        if a0.button()==Qt.LeftButton:
            self.setFocus()

    def initSetting(self):
        # 窗口中置
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)

        # 窗口禁止拉伸
        self.setFixedSize(self.width(), self.height())

        #禁用控件
        self.edit_btn.setEnabled(False)
        self.save_btn.setEnabled(False)
        self.apply_btn.setEnabled(False)
        self.tabWidget.setTabEnabled(1, False)
        self.tabWidget.setTabEnabled(2, False)

        #表初始化
        self.attr_table.verticalHeader().setVisible(False)
        self.attr_table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.attr_table.horizontalHeader().setStretchLastSection(True)
        self.attr_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.attr_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.attr_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.attr_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.attr_table.setShowGrid(False)

        self.selected_table.verticalHeader().setVisible(False)
        self.selected_table.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.selected_table.horizontalHeader().setStretchLastSection(True)
        self.selected_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.selected_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.selected_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.selected_table.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.selected_table.setShowGrid(False)


    def attachListener(self):
        self.open_btn.clicked.connect(self.openFile)
        self.attributePanel.m_TableModel.m_Table.cellClicked.connect(self.tableCellClick)
        self.edit_btn.clicked.connect(self.edit)

    def tableCellClick(self,row,column):
        self.attributeSummaryPanel.setAttribute(row)
        self.attributeVisualizationPanel.setAttribute(row)

    def edit(self):
        classIndex=self.attributeVisualizationPanel.getColoringIndex()
        cpInstance=Instances(self.m_Instances)
        cpInstance.setClassIndex(classIndex)
        self.dialog=ViewerDialog()
        self.dialog.resize(1000,600)
        self.dialog.setInstances(cpInstance)
        self.dialog.show()





if __name__ == '__main__':
    cgitb.enable(format='text')
    app = QApplication(sys.argv)
    MainWindow = PreprocessPanel()

    styleFile = './configuration/test.qss'
    with open(styleFile, 'r') as file:
        styleSheet = file.read()
        print(styleSheet)
    MainWindow.setStyleSheet(styleSheet)
    MainWindow.show()

    sys.exit(app.exec_())