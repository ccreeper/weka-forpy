from CallMain import MainWindow
from GenericObjectEditor import GenericObjectEditor
from Instances import Instances,Instance
from classifiers.Classifier import Classifier
from typing import *

class CalssifierPanel():
    def __init__(self,win:MainWindow):
        self.m_ClassifierEditor=GenericObjectEditor()
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

    def initalize(self):
        self.m_ClassifierEditor.setClassType(Classifier)
        # self.m_ClassifierEditor.setValue()

