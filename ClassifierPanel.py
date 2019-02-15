from GenericObjectEditor import GenericObjectEditor
from Instances import Instances,Instance
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PropertyPanel import PropertyPanel
from classifiers.Classifier import Classifier
from classifiers.rules.ZeroR import ZeroR
from classifier.SetInstancesPanel import SetInstancesPanel
from OptionHandler import OptionHandler
from Thread import Thread
from Utils import Utils
from typing import *
# import CallMain
import time
import copy

class ClassifierPanel():
    def __init__(self,win:'CallMain.MainWindow'):
        self.m_ClassifierEditor=GenericObjectEditor()
        self.m_Explor=win
        #TODO 中间条
        # self.m_CEPanel
        self.m_CEPanel=PropertyPanel(win,self.m_ClassifierEditor)
        self.m_OutText=win.outText              #type:QTextEdit
        #TODO 结果列表
        # self.m_History
        self.m_CVBut=win.cross_radio            #type:QRadioButton
        self.m_TrainBut=win.train_radio         #type:QRadioButton
        self.m_TestSplitBut=win.test_radio      #type:QRadioButton
        self.m_SetTestBut=win.test_set_btn      #type:QPushButton
        self.m_CVText=win.cross_value           #type:QLineEdit
        self.m_Instances=win.m_Instances        #type:Instances
        self.m_SetTestFrame=None                #type:SetInstancesPanel
        self.m_Thread=None                      #type:Thread
        self.m_StartBut=win.start_btn           #type:QPushButton
        self.m_StopBut=win.stop_btn             #type:QPushButton
        self.m_ClassCombo=win.classifier_combobox       #type:QComboBox
        self.m_TestClassIndex=-1
        self.mutex=QMutex()
        self.initalize()

    #TODO 未完成
    def initalize(self):
        self.m_OutText.setReadOnly(True)
        self.m_ClassifierEditor.setClassType(Classifier)
        self.m_ClassifierEditor.setValue(ZeroR())

        self.m_CVBut.clicked.connect(self.updateRadioLinks)
        self.m_TrainBut.clicked.connect(self.updateRadioLinks)
        self.m_TestSplitBut.clicked.connect(self.updateRadioLinks)
        self.m_SetTestBut.clicked.connect(self.setTestSet)
        # self.m_ClassifierEditor.setValue()

    def setTestSet(self):
        if self.m_SetTestFrame is None:
            if self.m_Explor is not None:
                preprocessPanel=self.m_Explor.getPreprocessPanel()
            else:
                raise Exception("We don't have access to a PreprocessPanel!")
            self.m_SetTestFrame=SetInstancesPanel(True,True)
            self.m_SetTestFrame.property_changed_signal.connect(self.propertyChanged)
        self.m_SetTestFrame.show()

    def propertyChanged(self,classIndex:int):
        self.m_TestClassIndex=classIndex

    def updateRadioLinks(self):
        self.m_SetTestBut.setEnabled(self.m_TestSplitBut.isChecked())
        if self.m_SetTestFrame is not None and not self.m_TestSplitBut.isChecked():
            self.m_SetTestFrame.setVisible(False)
        self.m_CVText.setEnabled(self.m_CVBut.isChecked())

    def startClassifier(self):
        if self.m_Thread is None:
            self.mutex.lock()
            self.m_StartBut.setEnabled(False)
            self.m_StopBut.setEnabled(True)
            self.mutex.unlock()

            # self.m_Thread=Thread()

    #TODO
    def threadClassifierRun(self):
        self.m_CEPanel.addToHistory()
        #CostMatrix costMatrix
        inst=Instances(self.m_Instances)
        trainTimeStart=trainTimeElapsed=testTimeStart=testTimeElapsed=0

        userTestStructure=copy.deepcopy(self.m_SetTestFrame.getInstances())    #type:Instances
        userTestStructure.setClassIndex(self.m_TestClassIndex)

        #默认outputmodel,output per-class stats,output confusion matrix,store predictions for visualization
        #outputPredictionsText=None
        numFolds=10
        classIndex=self.m_ClassCombo.currentIndex()
        inst.setClassIndex(classIndex)
        classifier=self.m_ClassifierEditor.getValue()
        template=copy.deepcopy(classifier)
        name=time.strftime("%H:%M:%S - ")

        if self.m_CVBut.isChecked():
            testMode=1
            numFolds=int(self.m_CVText.text())
            if numFolds<=1:
                raise Exception("Number of folds must be greater than 1")
            elif self.m_TrainBut.isChecked():
                testMode=3
            elif self.m_TestSplitBut.isChecked():
                testMode=4
                # if source is None:
                #     raise Exception("No user test set has been specified")
                if not inst.equalHeaders(userTestStructure):
                    QMessageBox.critical(self.m_Explor,"错误","测试数据集属性不同")
            else:
                raise Exception("Unknown test mode")
            cname=classifier.__module__
            if cname.startswith("classifiers."):
                name+=cname[len("classifiers."):]
            else:
                name+=cname
            cmd = classifier.__module__
            if isinstance(classifier,OptionHandler):
                cmd+=" "+Utils.joinOptions(classifier.getOptions())

            #TODO 1405

