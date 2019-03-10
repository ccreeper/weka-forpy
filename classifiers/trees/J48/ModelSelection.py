from typing import *
from classifiers.trees.J48.ClassifierSplitModel import ClassifierSplitModel
from Instances import Instances,Instance

class ModelSelection():
    def __init__(self,minNoObj:int,allData:Instances,useMDLcorrection:bool,
                 doNotMakeSplitPointActualValue:bool):
        self.m_minNoObj = minNoObj
        self.m_allData = allData
        self.m_useMDLcorrection = useMDLcorrection
        self.m_doNotMakeSplitPointActualValue = doNotMakeSplitPointActualValue

    def cleanup(self):
        self.m_allData=None

    def selectModel(self,data:Instances,test:Instances=None)->ClassifierSplitModel:...
