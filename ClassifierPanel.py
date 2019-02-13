from GenericObjectEditor import GenericObjectEditor
from Instances import Instances,Instance
from PropertyPanel import PropertyPanel
from classifiers.Classifier import Classifier
from classifiers.rules.ZeroR import ZeroR
from typing import *

class ClassifierPanel():
    def __init__(self,win:'MainWindow'):
        self.m_ClassifierEditor=GenericObjectEditor()
        self.m_ClassificationOutputPanel=PropertyPanel(win,self.m_ClassifierEditor)
        self.m_Explor=win
        #TODO 中间条
        # self.m_CEPanel
        self.m_CEPanel=win.outText
        #TODO 结果列表
        # self.m_History
        self.m_CVBut=win.cross_radio
        self.m_TrainBut=win.train_radio
        self.m_TestSplitBut=win.test_radio
        self.m_SetTestBut=win.test_set_btn
        self.m_CVText=win.cross_value
        self.m_Instances=win.m_Instances

        self.initalize()

    def initalize(self):
        self.m_ClassifierEditor.setClassType(Classifier)
        self.m_ClassifierEditor.setValue(ZeroR())


        # self.m_ClassifierEditor.setValue()

