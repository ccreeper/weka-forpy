from core.Instances import Instances

from classifiers.trees.J48Component.ClassifierTree import ClassifierTree
from classifiers.trees.J48Component.Distribution import Distribution
from classifiers.trees.J48Component.ModelSelection import ModelSelection
from classifiers.trees.J48Component.NoSplit import NoSplit
from core.Utils import Utils


class PruneableClassifierTree(ClassifierTree):
    def __init__(self,toSelectLocModel:ModelSelection,pruneTree:bool,num:int,cleanup:bool,seed:int):
        super().__init__(toSelectLocModel)
        self.pruneTheTree = pruneTree
        self.numSets = num
        self.m_cleanup = cleanup
        self.m_seed = seed

    def buildClassifier(self,data:Instances):
        data=Instances(data)
        data.deleteWithMissingClass()
        data.stratify(self.numSets)
        self.buildTree(data.trainCV(self.numSets,self.numSets-1,self.m_seed),
                       not self.m_cleanup,data.testCV(self.numSets,self.numSets-1))
        if self.pruneTheTree:
            self.prune()
        if self.m_cleanup:
            self.cleanup(Instances(data,0))

    def getNewTree(self,data:Instances,test:Instances=None):
        newTree=PruneableClassifierTree(self.m_toSelectModel,self.pruneTheTree,self.numSets,self.m_cleanup,self.m_seed)
        newTree.buildTree(data,not self.m_cleanup,test)
        return newTree

    def buildTree(self,data:Instances,keepData:bool,test:Instances=None):
        if keepData:
            self.m_train=data
        self.m_isLeaf=False
        self.m_isEmpty=False
        self.m_sons=None
        self.m_localModel=self.m_toSelectModel.selectModel(data,test)
        self.m_test=Distribution(test,self.m_localModel)
        if self.m_localModel.numSubsets() > 1:
            localTrain=self.m_localModel.split(data)
            localTest=self.m_localModel.split(test)
            self.m_sons=[]
            for i in range(len(self.m_sons)):
                self.m_sons.append(self.getNewTree(localTrain[i],localTest[i]))
                localTrain[i]=None
                localTest[i]=None
        else:
            self.m_isLeaf=True
            if Utils.equal(data.sumOfWeight(), 0):
                self.m_isEmpty=True


    def prune(self):
        if not self.m_isLeaf:
            for i in range(len(self.m_sons)):
                self.son(i).prune()
            if Utils.gr(self.errorsForTree(), self.errorsForLeaf()) or Utils.equal(self.errorsForTree(), self.errorsForLeaf()):
                self.m_sons=None
                self.m_isLeaf=None
                self.m_localModel=NoSplit(self.localModel().distribution())

    def errorsForTree(self):
        errors=0
        if self.m_isLeaf:
            return self.errorsForLeaf()
        for i in range(len(self.m_sons)):
            if Utils.equal(self.localModel().distribution().perBag(i), 0):
                errors+=self.m_test.perBag(i)-self.m_test.perClassPerBag(i,self.localModel().distribution().maxClass())
            else:
                errors+=self.son(i).errorsForTree()
        return errors

    def errorsForLeaf(self):
        return self.m_test.total()-self.m_test.perClass(self.localModel().distribution().maxClass())