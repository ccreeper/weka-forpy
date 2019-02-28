from typing import *
from Instances import Instances,Instance
from GenericObjectEditor import GenericObjectEditor
# from CallMain import MainWindow
from ResultHistoryPanel import ResultHistoryPanel
from PropertyPanel import PropertyPanel
from clusterers.SimpleKMeans import SimpleKMeans
from PyQt5.QtWidgets import *
from filters.attribute.Remove import Remove
from CapabilitiesHandler import CapabilitiesHandler
from SetInstancesPanel import SetInstancesPanel
from Capabilities import Capabilities,CapabilityEnum
from clusterers.Clusterer import Clusterer
from Thread import Thread


class ClustererPanel():
    def __init__(self,win:'MainWindow'):
        self.m_Explorer=win
        self.m_OutText=win.outText_cluster          #type:QTextEdit
        self.m_History=win.resultList_cluster   #type:ResultHistoryPanel
        self.m_TrainBut=win.train_radio_cluster     #type:QRadioButton
        self.m_TestSplitBut=win.test_radio_cluster  #type:QRadioButton
        self.m_SetTestBut=win.test_set_btn_cluster  #type:QPushButton
        self.m_StartBut=win.start_btn_cluster
        self.m_StopBut=win.stop_btn_cluster
        self.m_Option=win.option_cluster
        self.m_RunThread=None           #type:Thread
        self.m_SetTestFrame=None        #type:SetInstancesPanel
        self.m_ChooseBut=win.choose_cluster
        self.m_ClustererEditor=GenericObjectEditor()    #type:GenericObjectEditor
        self.m_CLPanel=PropertyPanel(self,self.m_ClustererEditor)    #type:PropertyPanel
        self.initalize()

    def initalize(self):
        self.m_OutText.setReadOnly(True)
        self.m_OutText.setLineWrapMode(QTextEdit.NoWrap)
        self.m_TrainBut.setChecked(True)
        self.m_StartBut.setEnabled(False)
        self.m_StopBut.setEnabled(False)

        self.m_ClustererEditor.setClassType(Clusterer)
        self.m_ClustererEditor.setValue(SimpleKMeans())

        self.m_TrainBut.clicked.connect(self.updateRadioLinks)
        self.m_TestSplitBut.clicked.connect(self.updateRadioLinks)
        self.m_SetTestBut.clicked.connect(self.setTestSet)
        # self.m_StartBut.clicked.connect(self.startClassifier)

    def startClassifier(self):
        pass
        # if self.m_RunThread is None:
        #     self.mutex.lock()
        #     self.m_StartBut.setEnabled(False)
        #     self.m_StopBut.setEnabled(True)
        #     self.mutex.unlock()
        #     self.m_RunThread=Thread(target=self.threadClassifierRun)
        #     self.m_RunThread.setPriority(QThread.LowPriority)
        #     self.m_RunThread.start()

    def getOptionBut(self):
        return self.m_Option

    def getChooseBut(self):
        return self.m_ChooseBut

    def setInstances(self,inst:Instances):
        self.m_Instances = inst


    def updateRadioLinks(self):
        self.m_SetTestBut.setEnabled(self.m_TestSplitBut.isChecked())
        if self.m_SetTestFrame is not None and not self.m_TestSplitBut.isChecked():
            self.m_SetTestFrame.setVisible(False)
        self.updateCapabilitiesFilter(self.m_ClustererEditor.getCapabilitiesFilter())


    def updateCapabilitiesFilter(self,filter:Capabilities):
        if filter is None:
            self.m_ClustererEditor.setCapabilitiesFilter(Capabilities(None))
            return
        tempInst=Instances(self.m_Instances)
        tempInst.setClassIndex(-1)
        #TODO Classes to clusters evaluation
        try:
            filterClass=Capabilities.forInstances(tempInst)
        except Exception:
            filterClass=Capabilities(None)
        self.m_ClustererEditor.setCapabilitiesFilter(filterClass)
        self.m_StartBut.setEnabled(True)
        currentFilter=self.m_ClustererEditor.getCapabilitiesFilter()
        clusterer=self.m_ClustererEditor.getValue()
        if clusterer is not None and currentFilter is not None and isinstance(clusterer,CapabilitiesHandler):
            currentSchemeCapabilities=clusterer.getCapabilities()       #type:Capabilities
            if not currentSchemeCapabilities.supportsMaybe(currentFilter) and not currentSchemeCapabilities.supports(currentFilter):
                self.m_StartBut.setEnabled(False)


    def setTestSet(self):
        if self.m_SetTestFrame is None:
            self.m_SetTestFrame=SetInstancesPanel()
        self.m_SetTestFrame.show()
