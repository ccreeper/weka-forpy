from classifiers.AbstractClassifier import AbstractClassifier
from typing import *
from Instances import Instances,Instance
from Utils import Utils
from Capabilities import Capabilities,CapabilityEnum
from classifiers.trees.J48Component.ClassifierTree import ClassifierTree
from classifiers.trees.J48Component.BinC45ModelSelection import BinC45ModelSelection
from classifiers.trees.J48Component.C45ModelSelection import C45ModelSelection
from classifiers.trees.J48Component.C45PruneableClassifierTree import C45PruneableClassifierTree
from classifiers.trees.J48Component.PruneableClassifierTree import PruneableClassifierTree

class J48(AbstractClassifier):
    propertyList=AbstractClassifier.propertyList[:]
    methodList=AbstractClassifier.methodList[:]
    def __init__(self):
        super().__init__()
        self.m_root=None        #type:ClassifierTree
        self.binarySplits=False
        self.collapseTree=True
        self.confidenceFactor=0.25
        self.minNumObj=2
        self.numFolds=3
        self.reducedErrorPruning=False
        self.seed=1
        self.subtreeRaising=True
        self.unpruned=False
        self.useLaplace=False
        self.useMDLcorrection=True
        self.noCleanup=False

    def __str__(self):
        if self.m_root is None:
            return "No classifier built"
        if self.unpruned:
            return "J48 unpruned tree\n------------------\n" + str(self.m_root)
        return "J48 pruned tree\n------------------\n" + str(self.m_root)

    def getCapabilities(self):
        result=Capabilities(self)
        result.disableAll()
        result.enable(CapabilityEnum.NOMINAL_ATTRIBUTES)
        result.enable(CapabilityEnum.NUMERIC_ATTRIBUTES)
        result.enable(CapabilityEnum.DATE_ATTRIBUTES)
        result.enable(CapabilityEnum.MISSING_VALUES)
        result.enable(CapabilityEnum.NOMINAL_CLASS)
        result.enable(CapabilityEnum.MISSING_CLASS_VALUES)

        result.setMinimumNumberInstances(0)
        return result

    def distributionForInstance(self,instance:Instance):
        return self.m_root.distributionForInstance(instance,self.useLaplace)

    def buildClassifier(self,data:Instances):
        self.getCapabilities().testWithFail(data)
        if self.binarySplits:
            modSelection=BinC45ModelSelection(self.minNumObj,data,self.useMDLcorrection,self.doNotCheckCapabilities)
        else:
            modSelection=C45ModelSelection(self.minNumObj,data,self.useMDLcorrection,self.doNotCheckCapabilities)
        if not self.reducedErrorPruning:
            self.m_root=C45PruneableClassifierTree(modSelection, not self.unpruned, self.confidenceFactor,
                                                   self.subtreeRaising, not self.noCleanup,
                                                   self.collapseTree)
        else:
            self.m_root=PruneableClassifierTree(modSelection,not self.unpruned,self.numFolds,not self.noCleanup,self.seed)
        self.m_root.buildClassifier(data)
        modSelection.cleanup()
