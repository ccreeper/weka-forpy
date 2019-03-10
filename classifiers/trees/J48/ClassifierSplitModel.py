from typing import *
from Instances import Instances,Instance
from classifiers.trees.J48.Distribution import Distribution
from classifiers.trees.J48.InfoGainSplitCrit import InfoGainSplitCrit
from classifiers.trees.J48.GainRatioSplitCrit import GainRatioSplitCrit
from Utils import Utils

class ClassifierSplitModel():
    infoGainCrit=InfoGainSplitCrit()
    gainRatioCrit=GainRatioSplitCrit()

    def __init__(self,attIndex:int,minNoObj:int,sumOfWeights:float,useMDLcorrection:bool):
        self.m_distribution=None    #type:Distribution
        self.m_numSubsets=0
        self.m_attIndex=attIndex
        self.m_minNoObj=minNoObj
        self.m_sumOfWeights=sumOfWeights
        self.m_useMDLcorrection=useMDLcorrection

        self.m_numSubsets=0
        self.m_splitPoint=float("inf")
        self.m_infoGain=0
        self.m_gainRatio=0

    def classProb(self,classIndex:int,instance:Instance,theSubset:int):
        if theSubset > -1:
            return self.m_distribution.prob(classIndex,theSubset)
        else:
            weights=self.weights(instance)
            if weights is None:
                return self.m_distribution.prob(classIndex)
            else:
                prob=0
                for i in range(len(weights)):
                    prob+=weights[i]*self.m_distribution.prob(classIndex,i)
                return prob

    def numSubsets(self):
        return self.m_numSubsets

    def dumpLabel(self,index:int,data:Instances):
        text=""
        text+=data.classAttribute().value(self.m_distribution.maxClass(index))
        text+=" ("+Utils.roundDouble(self.m_distribution.perBag(index),2)
        if Utils.gr(self.m_distribution.numIncorrect(index),0):
            text+="/"+Utils.roundDouble(self.m_distribution.numIncorrect(index),2)
        text+=")"
        return text

    def split(self,data:Instances)->List[Instances]:
        subsetSize=[0]*self.m_numSubsets
        for inst in data:
            subset=self.whichSubset(inst)
            if subset > -1:
                subsetSize[subset]+=1
            else:
                weights=self.weights(inst)
                for j in range(self.m_numSubsets):
                    if Utils.gr(weights[j],0):
                        subsetSize[j]+=1
        instances=[]        #type:List[Instances]
        for j in range(self.m_numSubsets):
            instances.append(Instances(data,subsetSize[j]))
        for inst in data:
            subset=self.whichSubset(inst)
            if subset > -1:
                instances[subset].add(inst)
            else:
                weights=self.weights(inst)
                for j in range(self.m_numSubsets):
                    if Utils.gr(weights[j],0):
                        instances[j].add(inst)
                        instances[j].lastInstance().setWeight(weights[j]*inst.weight())
        return instances

    def classProbLaplace(self,classIndex:int,instance:Instance,theSubset:int):
        if theSubset > -1:
            return self.m_distribution.laplaceProb(classIndex,theSubset)
        else:
            weights=self.weights(instance)
            if weights is None:
                return self.m_distribution.laplaceProb(classIndex)
            else:
                prob=0
                for i in range(len(weights)):
                    prob+=weights[i]*self.m_distribution.laplaceProb(classIndex,i)
                return prob

    def distribution(self):
        return self.m_distribution

    def checkModel(self):
        if self.m_numSubsets > 0:
            return True
        return False

    def attIndex(self):
        return self.m_attIndex

    def splitPoint(self):
        return self.m_splitPoint

    def weights(self,instance:Instance):
        if instance.isMissing(self.m_attIndex):
            weights=[]
            for i in range(self.m_numSubsets):
                weights.append(self.m_distribution.perBag(i)/self.m_distribution.total())
            return weights
        return None

    def setSplitPoint(self,allInstances:Instances):
        newSplitPoint=float("-inf")
        if allInstances.attribute(self.m_attIndex).isNumeric() and self.m_numSubsets > 1:
            for i in range(allInstances.numInstances()):
                instance=allInstances.instance(i)
                tempValue=instance.value(self.m_attIndex)
                if not Utils.isMissingValue(tempValue):
                    if tempValue > newSplitPoint and tempValue <= self.m_splitPoint:
                        newSplitPoint=tempValue
            self.m_splitPoint=newSplitPoint

    def infoGain(self):
        return self.m_infoGain

    def gainRatio(self):
        return self.m_gainRatio

    def leftSide(self,data:Instances):
        return data.attribute(self.m_attIndex).name()

    def resetDistribution(self,data:Instances):
        self.m_distribution=Distribution(data,self)

    def whichSubset(self,instance:Instance)->int:...
    def rightSide(self,index:int,data:Instances)->str:...
    def buildClassifer(self,instances:Instances):...
