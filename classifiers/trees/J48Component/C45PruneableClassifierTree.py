from typing import *
from classifiers.trees.J48Component.ClassifierTree import ClassifierTree
from classifiers.trees.J48Component.ModelSelection import ModelSelection
from classifiers.trees.J48Component.NoSplit import NoSplit
from classifiers.trees.J48Component.Distribution import Distribution
from Instances import Instances,Instance
from Utils import Utils

class C45PruneableClassifierTree(ClassifierTree):
    def __init__(self,toSelectLocModel:ModelSelection,pruneTree:bool,
                 cf:float,raiseTree:bool,cleanup:bool,collapseTree:bool):
        super().__init__(toSelectLocModel)
        self.m_pruneTheTree=pruneTree
        self.m_CF=cf
        self.m_subtreeRaising=raiseTree
        self.m_cleanup=cleanup
        self.m_collapseTheTree=collapseTree

    def buildClassifier(self,data:Instances):
        data=Instances(data)
        data.deleteWithMissingClass()
        self.buildTree(data,self.m_subtreeRaising or not self.m_cleanup)
        if self.m_collapseTheTree:
            self.collapse()
        if self.m_pruneTheTree:
            self.prune()
        if self.m_cleanup:
            self.cleanup(Instances(data,0))


    def collapse(self):
        if not self.m_isLeaf:
            errorsOfSubtree=self.getTrainingErrors()
            errorsOfTree=self.localModel().distribution().numIncorrect()
            if errorsOfSubtree >= errorsOfTree-1e-3:
                self.m_sons=None
                self.m_isLeaf=True
                self.m_localModel=NoSplit(self.localModel().distribution())
            else:
                for i in range(len(self.m_sons)):
                    self.son(i).collapse()

    def prune(self):
        if not self.m_isLeaf:
            for i in range(len(self.m_sons)):
                self.son(i).prune()
            indexOfLargestBranch=self.localModel().distribution().maxBag()
            if self.m_subtreeRaising:
                errorsLargestBranch=self.son(indexOfLargestBranch).getEstimatedErrorsForBranch(self.m_train)
            else:
                errorsLargestBranch=float("inf")
            errorsLeaf=self.getEstimatedErrorsForDistribution(self.localModel().distribution())
            errorsTree=self.getEstimatedErrors()
            if (Utils.gr(errorsTree+0.1,errorsLeaf) or Utils.equal(errorsTree+0.1,errorsLeaf)) and\
                (Utils.gr(errorsLargestBranch+0.1,errorsLeaf) or Utils.equal(errorsLargestBranch+0.1,errorsLeaf)):
                self.m_sons=None
                self.m_isLeaf=True
                self.m_localModel=NoSplit(self.localModel().distribution())
                return
            if Utils.gr(errorsTree+0.1,errorsLargestBranch) or Utils.equal(errorsTree+0.1,errorsLargestBranch):
                largestBranch=self.son(indexOfLargestBranch)
                self.m_sons=largestBranch.m_sons
                self.m_localModel=largestBranch.localModel()
                self.m_isLeaf=largestBranch.m_isLeaf
                self.newDistribution(self.m_train)
                self.prune()


    def newDistribution(self,data:Instances):
        self.localModel().resetDistribution(data)
        self.m_train=data
        if not self.m_isLeaf:
            localInstances=self.localModel().split(data)
            for i in range(len(self.m_sons)):
                self.son(i).newDistribution(localInstances[i])
        else:
            if not Utils.equal(data.sumOfWeight(),0):
                self.m_isEmpty=False


    def getEstimatedErrors(self):
        errors=0
        if self.m_isLeaf:
            return self.getEstimatedErrorsForDistribution(self.localModel().distribution())
        else:
            for i in range(len(self.m_sons)):
                errors=errors+self.son(i).getEstimatedErrors()
            return errors

    def getEstimatedErrorsForBranch(self,data:Instances):
        errors=0
        if self.m_isLeaf:
            return self.getEstimatedErrorsForDistribution(Distribution(data))
        saveDist=self.localModel().m_distribution
        self.localModel().resetDistribution(data)
        localInstances=self.localModel().split(data)
        self.localModel().m_distribution=saveDist
        for i in range(len(self.m_sons)):
            errors=errors+self.son(i).getEstimatedErrorsForBranch(localInstances[i])
        return errors

    def getEstimatedErrorsForDistribution(self,theDistribution:Distribution):
        if Utils.equal(theDistribution.total(),0):
            return 0
        return theDistribution.numIncorrect()+Utils.addErrs(theDistribution.total(),theDistribution.numIncorrect(),self.m_CF)

    def getTrainingErrors(self):
        errors=0
        if self.m_isLeaf:
            return self.localModel().distribution().numIncorrect()
        else:
            for i in range(len(self.m_sons)):
                errors=errors+self.son(i).getTrainingErrors()
            return errors

    def getNewTree(self,data:Instances,test:Instances=None):
        newTree=C45PruneableClassifierTree(self.m_toSelectModel,self.m_pruneTheTree,self.m_CF,self.m_subtreeRaising,self.m_cleanup,self.m_collapseTheTree)
        newTree.buildTree(data,self.m_subtreeRaising or not self.m_cleanup)
        print("c45 new")
        return newTree