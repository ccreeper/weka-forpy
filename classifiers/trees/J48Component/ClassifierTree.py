from typing import *

from core.CapabilitiesHandler import CapabilitiesHandler
from core.Drawable import Drawable
from core.Instances import Instances, Instance

from classifiers.trees.J48Component.ClassifierSplitModel import ClassifierSplitModel
from classifiers.trees.J48Component.Distribution import Distribution
from classifiers.trees.J48Component.ModelSelection import ModelSelection
from core.Utils import Utils


class ClassifierTree(CapabilitiesHandler,Drawable):
    def __init__(self,toSelectLocModel:ModelSelection):
        self.m_toSelectModel=toSelectLocModel       #type:ModelSelection
        self.m_localModel=None          #type:ClassifierSplitModel
        self.m_sons=None        #type:List[ClassifierTree]
        self.m_isLeaf=False
        self.m_isEmpty=False
        self.m_train=None       #type:Instances
        self.m_test=None    #type:Distribution
        self.m_id=0

    def __str__(self):
        text=""
        if self.m_isLeaf:
            text+=": "
            text+=self.m_localModel.dumpLabel(0,self.m_train)
        else:
            text=self.dumpTree(0,text)
        text+="\n\nNumber of Leaves  : \t" + str(self.numLeaves()) + "\n"
        text+="\nSize of the tree : \t" + str(self.numNodes()) + "\n"
        return text

    def numLeaves(self):
        num=0
        if self.m_isLeaf:
            return 1
        for i in range(len(self.m_sons)):
            num+=self.m_sons[i].numLeaves()
        return num

    def graphType(self):
        return Drawable.TREE

    def graph(self):
        text="{"
        # self.assignIDs(-1)
        # text+="digraph J48Tree {\n"
        if self.m_isLeaf:
            text+='"' + Utils.backQuoteChars(self.m_localModel.dumpLabel(0, self.m_train)) + '"'
            # if self.m_train is not None and self.m_train.numInstances() > 0:
            #     text+="data =\n" + str(self.m_train) + "\n"
            #     text+=",\n"
            # text+="]\n"
        else:
            text+='"' + Utils.backQuoteChars(self.m_localModel.leftSide(self.m_train)) + '":'
            # if self.m_train is not None and self.m_train.numInstances() > 0:
            #     text+="data =\n" + str(self.m_train) + "\n"
            #     text+=",\n"
            # text+=']\n'
            text=self.graphTree(text)
        text+="}"
        return text


    def assignIDs(self,lastID:int):
        currLastID=lastID+1
        self.m_id=currLastID
        if self.m_sons is not None:
            for son in self.m_sons:
                currLastID=son.assignIDs(currLastID)
        return currLastID

    def numNodes(self):
        no=1
        if not self.m_isLeaf:
            for i in range(len(self.m_sons)):
                no+=self.m_sons[i].numNodes()
        return no

    def dumpTree(self,depth:int,text:str):
        for i in range(len(self.m_sons)):
            text+="\n"
            for j in range(depth):
                text+="|   "
            text+=self.m_localModel.leftSide(self.m_train)
            text+=self.m_localModel.rightSide(i,self.m_train)
            if self.m_sons[i].m_isLeaf:
                text+=": "
                text+=self.m_localModel.dumpLabel(i,self.m_train)
            else:
                text=self.m_sons[i].dumpTree(depth+1,text)
        return text


    def distributionForInstance(self,instance:Instance,useLaplace:bool):
        numbers=[]
        for i in range(instance.numClasses()):
            if not useLaplace:
                numbers.append(self.getProbs(i,instance,1))
            else:
                numbers.append(self.getProbsLaplace(i,instance,1))
        return numbers

    def buildClassifier(self,data:Instances):
        data=Instances(data)
        data.deleteWithMissingClass()
        self.buildTree(data,False)

    def buildTree(self,data:Instances,keepData:bool,test:Instances=None):
        if keepData:
            self.m_train = data
        self.m_isLeaf = False
        self.m_isEmpty = False
        self.m_sons = None
        if test is None:
            self.m_test=None
            self.m_localModel = self.m_toSelectModel.selectModel(data)
            if self.m_localModel.numSubsets() > 1:
                localInstances=self.m_localModel.split(data)
                self.m_sons=[]
                for i in range(self.m_localModel.numSubsets()):
                    self.m_sons.append(self.getNewTree(localInstances[i]))
                    localInstances[i]=None
            else:
                self.m_isLeaf=True
                if Utils.equal(data.sumOfWeight(), 0):
                    self.m_isEmpty=True

        else:
            self.m_localModel=self.m_toSelectModel.selectModel(data,test)
            self.m_test=Distribution(test,self.m_localModel)
            if self.m_localModel.numSubsets() > 1:
                localTrain=self.m_localModel.split(data)
                localTest=self.m_localModel.split(test)
                self.m_sons=[]
                for i in range(self.m_localModel.numSubsets()):
                    self.m_sons.append(self.getNewTree(localTrain[i],localTest[i]))
                    localTrain[i]=None
                    localTest[i]=None
            else:
                self.m_isLeaf=True
                if Utils.equal(data.sumOfWeight(), 0):
                    self.m_isEmpty=True

    def getNewTree(self,data:Instances,test:Instances=None):
        newTree=ClassifierTree(self.m_toSelectModel)
        if test is None:
            newTree.buildTree(data,False)
        else:
            newTree.buildTree(data,False,test)
        return newTree

    def getProbsLaplace(self,classIndex:int,instance:Instance,weight:float):
        prob=0
        if self.m_isLeaf:
            return weight*self.localModel().classProbLaplace(classIndex,instance,-1)
        else:
            treeIndex=self.localModel().whichSubset(instance)
            if treeIndex == -1:
                weights=self.localModel().weights(instance)
                for i in range(len(self.m_sons)):
                    if not self.son(i).m_isEmpty:
                        prob+=self.son(i).getProbsLaplace(classIndex,instance,weights[i]*weight)
                return prob
            else:
                if self.son(treeIndex).m_isEmpty:
                    return weight*self.localModel().classProbLaplace(classIndex,instance,treeIndex)
                return self.son(treeIndex).getProbsLaplace(classIndex,instance,weight)

    def getProbs(self,classIndex:int,instance:Instance,weight:float):
        prob=0
        if self.m_isLeaf:
            return weight*self.localModel().classProb(classIndex,instance,-1)
        else:
            treeIndex=self.localModel().whichSubset(instance)
            if treeIndex == -1:
                weights=self.localModel().weights(instance)
                for i in range(len(self.m_sons)):
                    if not self.son(i).m_isEmpty:
                        prob+=self.son(i).getProbs(classIndex,instance,weights[i]*weight)
                return prob
            else:
                if self.son(treeIndex).m_isEmpty:
                    return weight*self.localModel().classProb(classIndex,instance,treeIndex)
                return self.son(treeIndex).getProbs(classIndex,instance,weight)

    def cleanup(self,justHeaderInfo:Instances):
        self.m_train=justHeaderInfo
        if not self.m_isLeaf:
            for son in self.m_sons:
                son.cleanup(justHeaderInfo)

    def graphTree(self,text:str):
        text+="{"
        for i in range(len(self.m_sons)):
            if i != 0:
                text+=","
            text+='"' + Utils.backQuoteChars(self.m_localModel.rightSide(i, self.m_train).strip()) + '":'
            if self.m_sons[i].m_isLeaf:
                text+='"' + Utils.backQuoteChars(self.m_localModel.dumpLabel(i, self.m_train)) + '"'
                # if self.m_train is not None and self.m_train.numInstances() > 0:
                #     text+="data =\n" + str(self.m_sons[i].m_train) + "\n,\n"
                # text+="]\n"
            else:
                text+='{'
                text+='"' + Utils.backQuoteChars(self.m_sons[i].m_localModel.leftSide(self.m_train)) + '":'
                # if self.m_train is not None and self.m_train.numInstances() > 0:
                #     text+="data =\n" + str(self.m_sons[i].m_train) + "\n,\n"
                # text+=']\n'
                text=self.m_sons[i].graphTree(text)
                text+="}"
        text+="}"
        return text

    def son(self,index:int):
        return self.m_sons[index]

    def localModel(self)->ClassifierSplitModel:
        return self.m_localModel
