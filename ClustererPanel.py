from typing import *
from Instances import Instances,Instance
from ClustererAssignmentsPlotInstances import ClustererAssignmentsPlotInstances
from GenericObjectEditor import GenericObjectEditor,GOEPanel
# from CallMain import MainWindow
from ResultHistoryPanel import ResultHistoryPanel
from filters.Filter import Filter
from PropertyPanel import PropertyPanel
from clusterers.SimpleKMeans import SimpleKMeans
from clusterers.ClusterEvaluation import ClusterEvaluation
from PyQt5.QtWidgets import *
from filters.attribute.Remove import Remove
from CapabilitiesHandler import CapabilitiesHandler
from SetInstancesPanel import SetInstancesPanel
from Capabilities import Capabilities,CapabilityEnum
from clusterers.Clusterer import Clusterer
from Thread import Thread
from OptionHandler import OptionHandler
from PyQt5.QtCore import *
from Utils import Utils
import time
import copy


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
        self.m_History.outtext_write_signal.connect(self.updateOutputText)
        self.initalize()

    def updateOutputText(self,text:str):
        self.m_OutText.setText(text)

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
        self.m_StartBut.clicked.connect(self.startClusterer)

    def startClusterer(self):
        if self.m_RunThread is None:
            self.m_StartBut.setEnabled(False)
            self.m_StopBut.setEnabled(True)
            self.m_RunThread=Thread(target=self.clusterRunThread)
            self.m_RunThread.setPriority(QThread.LowPriority)
            self.m_RunThread.start()

    def clusterRunThread(self):
        self.m_CLPanel.addToHistory()
        inst=Instances(self.m_Instances)
        inst.setClassIndex(-1)
        plotInstances=ClustererAssignmentsPlotInstances()
        plotInstances.setClusterer(self.m_ClustererEditor.getValue())
        userTest=None
        if self.m_SetTestFrame is not None:
            if self.m_SetTestFrame.getInstances() is not None:
                userTest=Instances(self.m_SetTestFrame.getInstances())
        clusterer=self.m_ClustererEditor.getValue()
        outBuff=""
        name=time.strftime("%H:%M:%S - ")
        cname=clusterer.__module__
        if cname.startswith("clusterers."):
            name+=cname[len("clusterers."):]
        else:
            name+=cname
        if self.m_TrainBut.isChecked():
            testMode=0
        elif self.m_TestSplitBut.isChecked():
            testMode=1
            if userTest is None:
                raise Exception("No user test set has been opened")
            if not inst.equalHeaders(userTest):
                raise Exception("Train and test set are not compatible\n"+ inst.equalHeadersMsg(userTest))
        else:
            raise Exception("Unknown test mode")
        trainInst=Instances(inst)
        outBuff+="=== Run information ===\n\n"
        outBuff+="Scheme:       " + cname
        outBuff+="\n"
        outBuff+="Relation:     " + inst.relationName() + '\n'
        outBuff+="Instances:    " + str(inst.numInstances()) + '\n'
        outBuff+="Attributes:   " + str(inst.numAttributes()) + '\n'
        if inst.numAttributes() < 100:
            for i in range(inst.numAttributes()):
                outBuff+="              " + inst.attribute(i).name()+ '\n'
        else:
            outBuff+="              [list of attributes omitted]\n"
        outBuff+="Test mode:    "
        if testMode == 0:
            outBuff+="evaluate on training data\n"
        elif testMode == 1:
            "user supplied test set: "+ str(userTest.numInstances()) + " instances\n"
        outBuff+='\n'
        self.m_History.addResult(name,outBuff)
        self.m_History.setSingle(name)
        trainTimeStart=time.time()
        if isinstance(clusterer,Clusterer):
            clusterer.buildClusterer(self.removeClass(trainInst))
        trainTimeElapsed=time.time()-trainTimeStart
        outBuff+="\n=== Clustering model (full training set) ===\n\n"
        outBuff+=str(clusterer)+'\n'
        outBuff+="\nTime taken to build model (full training data) : "\
                + Utils.doubleToString(trainTimeElapsed / 1000.0, 2)\
                + " seconds\n\n"
        self.m_History.updateResult(name,outBuff)
        evaluation=ClusterEvaluation()
        evaluation.setClusterer(clusterer)
        if testMode == 0:
            evaluation.evaluateClusterer(trainInst,False)
            plotInstances.setInstances(inst)
            plotInstances.setClusterEvaluation(evaluation)
            outBuff+="=== Model and evaluation on training set ===\n\n"
        elif testMode == 1:
            userTestT=Instances(userTest)
            evaluation.evaluateClusterer(userTestT,False)
            plotInstances.setInstances(userTest)
            plotInstances.setClusterEvaluation(evaluation)
            outBuff+="=== Evaluation on test set ===\n"
        else:
            raise Exception("Test mode not implemented")
        outBuff+=evaluation.clusterResultsToString()
        outBuff+='\n'
        self.m_History.updateResult(name,outBuff)

        #TODO right-click visizalition
        if plotInstances is not None and plotInstances.canPlot(True):
            pass
        self.m_RunThread=None
        self.m_StartBut.setEnabled(True)
        self.m_StopBut.setEnabled(False)
        Utils.debugOut(outBuff)

    def removeClass(self,inst:Instances):
        af=Remove()
        if inst.classIndex() < 0:
            retI=inst
        else:
            af.setAttributeIndices("" + str(inst.classIndex() + 1))
            af.setInvertSelection(False)
            af.setInputFormat(inst)
            retI=Filter.useFilter(inst,af)
        return retI


    def getOptionBut(self):
        return self.m_Option

    def getChooseBut(self):
        return self.m_ChooseBut

    def setInstances(self,inst:Instances):
        self.m_Instances = inst
        self.m_StartBut.setEnabled(self.m_RunThread is None)
        self.m_StopBut.setEnabled(self.m_RunThread is not None)
        self.updateRadioLinks()


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
