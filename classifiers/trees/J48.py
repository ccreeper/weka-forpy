from core.Capabilities import Capabilities, CapabilityEnum
from core.Instances import Instances, Instance

from classifiers.AbstractClassifier import AbstractClassifier
from classifiers.trees.J48Component.BinC45ModelSelection import BinC45ModelSelection
from classifiers.trees.J48Component.C45ModelSelection import C45ModelSelection
from classifiers.trees.J48Component.C45PruneableClassifierTree import C45PruneableClassifierTree
from classifiers.trees.J48Component.ClassifierTree import ClassifierTree
from classifiers.trees.J48Component.PruneableClassifierTree import PruneableClassifierTree
from core.Drawable import Drawable


class J48(AbstractClassifier,Drawable):
    propertyList={"binarySplits":"False","confidenceFactor":"0.25","minNumObj":"2","unpruned":"False"}
    methodList={"binarySplits":"setBinarySplits","confidenceFactor":"setConfidenceFactor","minNumObj":"setMinNumObj","unpruned":"setUnpruned"}

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

    def graphType(self):
        return Drawable.TREE

    def graph(self):
        return self.m_root.graph()

    def distributionForInstance(self,instance:Instance):
        return self.m_root.distributionForInstance(instance,self.useLaplace)

    def setBinarySplits(self,value:int):
        if value == 0:
            self.binarySplits=False
        else:
            self.binarySplits=True

    def setUnpruned(self,value:int):
        if value == 0:
            self.unpruned=False
        else:
            self.unpruned=True

    def setConfidenceFactor(self,value:str):
        try:
            val=float(value)
            self.confidenceFactor=val
            self.propertyList.update({"confidenceFactor":value})
        except ValueError:
            pass

    def setMinNumObj(self,value:str):
        try:
            val=float(value)
            self.minNumObj=val
            self.propertyList.update({"minNumObj":value})
        except ValueError:
            pass

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
