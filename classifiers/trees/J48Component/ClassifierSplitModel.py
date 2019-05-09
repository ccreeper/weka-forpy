from typing import *

from core.Instances import Instances, Instance

from classifiers.trees.J48Component.GainRatioSplitCrit import Distribution
from classifiers.trees.J48Component.GainRatioSplitCrit import GainRatioSplitCrit
from classifiers.trees.J48Component.InfoGainSplitCrit import InfoGainSplitCrit
from core.Utils import Utils


class ClassifierSplitModel():
    infoGainCrit=InfoGainSplitCrit()
    gainRatioCrit=GainRatioSplitCrit()

    def __init__(self):
        self.m_distribution=None    #type:Distribution
        self.m_numSubsets=0

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
        text+=" ("+str(Utils.roundDouble(self.m_distribution.perBag(index), 2))
        if Utils.gr(self.m_distribution.numIncorrect(index), 0):
            text+="/"+str(Utils.roundDouble(self.m_distribution.numIncorrect(index), 2))
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
                    if Utils.gr(weights[j], 0):
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
                    if Utils.gr(weights[j], 0):
                        instances[j].add(inst)
                        instances[j].lastInstance().setWeight(float(weights[j]*inst.weight()))
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

    def checkModel(self):
        if self.m_numSubsets > 0:
            return True
        return False

    def distribution(self):
        return self.m_distribution

    def resetDistribution(self,data:Instances):
        self.m_distribution=Distribution(data,self)

    def leftSide(self,data:Instances)->str:...
    def weights(self,instance:Instance)->List[float]:...
    def whichSubset(self,instance:Instance)->int:...
    def rightSide(self,index:int,data:Instances)->str:...
    def buildClassifer(self,instances:Instances):...
