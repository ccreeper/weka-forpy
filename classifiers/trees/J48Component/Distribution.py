from typing import *

from core.Instances import Instances, Instance

import classifiers.trees.J48Component.ClassifierSplitModel
from core.Utils import Utils


class Distribution():
    @overload
    def __init__(self,numBags:int,numClasses:int):
        self.m_perClassPerBag=None
        self.m_perBag=None
        self.m_perClass=None
        self.totaL=0
    @overload
    def __init__(self,table:List[List[float]]):...
    @overload
    def __init__(self,source:Instances):...
    @overload
    def __init__(self,source:Instances,modelToUse:'ClassifierSplitModel'):...
    @overload
    def __init__(self,toMerge:'Distribution'):...
    @overload
    def __init__(self,toMerge:'Distribution',index:int):...

    def __init__(self, a0,a1=None):
        if isinstance(a0,int) and isinstance(a1,int):
            self.m_perClassPerBag=[]
            self.m_perBag= [0] * a0
            self.m_perClass= [0] * a1
            for i in range(a0):
                self.m_perClassPerBag.append([0] * a1)
            self.totaL=0
        elif isinstance(a0,list):
            self.m_perClassPerBag=a0
            self.m_perBag=[0]*len(a0)
            self.m_perClass=[0]*len(a0[0])
            for i in range(len(a0)):
                for j in range(len(a0[i])):
                    self.m_perBag[i]+=a0[i][j]
                    self.m_perClass[j]+=a0[i][j]
                    self.totaL+=a0[i][j]
        elif isinstance(a0,Instances) and a1 is None:
            self.m_perClassPerBag=[[0]*a0.numClasses()]
            self.m_perBag=[0]
            self.totaL=0
            self.m_perClass=[0]*a0.numClasses()
            for inst in a0:
                self.add(0,inst)
        elif isinstance(a0,Instances) and isinstance(a1,classifiers.trees.J48Component.ClassifierSplitModel.ClassifierSplitModel):
            self.m_perClassPerBag=[[0]*a0.numClasses() for k in range(a1.numSubsets())]
            self.m_perBag=[0]*a1.numSubsets()
            self.totaL=0
            self.m_perClass=[0]*a0.numClasses()
            for inst in a0:
                index=a1.whichSubset(inst)
                if index != -1:
                    self.add(index,inst)
                else:
                    weights=a1.weights(inst)
                    self.addWeights(inst,weights)
        elif isinstance(a0,Distribution) and a1 is None:
            self.totaL=a0.totaL
            self.m_perClass=a0.m_perClass[:]
            self.m_perClassPerBag=[[0]*a0.numClasses()]
            self.m_perBag=[self.totaL]
        elif isinstance(a0,Distribution) and isinstance(a1,int):
            self.totaL=a0.totaL
            self.m_perClass=a0.m_perClass[:]
            self.m_perClassPerBag=[a0.m_perClassPerBag[a1][:],[0]*a0.numClasses()]
            for i in range(a0.numClasses()):
                self.m_perClassPerBag[1][i]=a0.m_perClass[i]-self.m_perClassPerBag[0][i]
            self.m_perBag=[0,0]
            self.m_perBag[0]=a0.m_perBag[a1]
            self.m_perBag[1]=self.totaL-self.m_perBag[0]

    def addWeights(self,instance:Instance,weights:List):
        classIndex=int(instance.classValue())
        for i in range(len(self.m_perBag)):
            weight=instance.weight()*weights[i]
            self.m_perClassPerBag[i][classIndex]=self.m_perClassPerBag[i][classIndex]+weight
            self.m_perBag[i]=self.m_perBag[i]+weight
            self.m_perClass[classIndex]=self.m_perClass[classIndex]+weight
            self.totaL+=weight


    def add(self,bagIndex:int,instance:Instance):
        classIndex=int(instance.classValue())
        weight=instance.weight()
        self.m_perClassPerBag[bagIndex][classIndex]=self.m_perClassPerBag[bagIndex][classIndex]+weight
        self.m_perBag[bagIndex]=self.m_perBag[bagIndex]+weight
        self.m_perClass[classIndex]=self.m_perClass[classIndex]+weight
        self.totaL+=weight

    def check(self,minNoObj:float):
        counter=0
        for i in range(len(self.m_perBag)):
            if Utils.gr(self.m_perBag[i], minNoObj) or Utils.equal(self.m_perBag[i], minNoObj):
                counter+=1
                if counter > 1:
                    return True
        return False

    def perClassPerBag(self,bagIndex:int,classIndex:int):
        return self.m_perClassPerBag[bagIndex][classIndex]

    def addRange(self,bagIndex:int,source:Instances,startIndex:int,lastPlusOne:int):
        sumOfWeights=0
        for i in range(startIndex,lastPlusOne):
            instance=source.instance(i)
            classIndex=int(instance.classValue())
            sumOfWeights+=instance.weight()
            self.m_perClassPerBag[bagIndex][classIndex]+=instance.weight()
            self.m_perClass[classIndex]+=instance.weight()
        self.m_perBag[bagIndex]+=sumOfWeights
        self.totaL+=sumOfWeights

    def maxBag(self):
        max=0
        maxIndex=-1
        for i in range(len(self.m_perBag)):
            if Utils.gr(self.m_perBag[i], max) or Utils.equal(self.m_perBag[i], max):
                max=self.m_perBag[i]
                maxIndex=i
        return maxIndex

    def shiftRange(self,begin:int,end:int,source:Instances,startIndex:int,lastPlusOne:int):
        for i in range(startIndex,lastPlusOne):
            instance=source.instance(i)
            classIndex=int(instance.classValue())
            weight=instance.weight()
            self.m_perClassPerBag[begin][classIndex]-=weight
            self.m_perClassPerBag[end][classIndex]+=weight
            self.m_perBag[begin]-=weight
            self.m_perBag[end]+=weight


    def addInstWithUnknown(self,source:Instances,attIndex:int):
        probs=[]
        for j in range(len(self.m_perBag)):
            if Utils.equal(self.totaL, 0):
                probs.append(1/len(self.m_perBag))
            else:
                probs.append(self.m_perBag[j]/self.totaL)
        for inst in source:
            if inst.isMissing(attIndex):
                classIndex=int(inst.classValue())
                weight=inst.weight()
                self.m_perClass[classIndex]=self.m_perClass[classIndex]+weight
                self.totaL=self.totaL+weight
                for j in range(len(self.m_perBag)):
                    newWeight=probs[j]*weight
                    self.m_perClassPerBag[j][classIndex]=self.m_perClassPerBag[j][classIndex]+newWeight
                    self.m_perBag[j]=self.m_perBag[j]+newWeight


    def prob(self,classIndex:int,intIndex:int=None):
        if intIndex is None:
            if not Utils.equal(self.totaL, 0):
                return self.m_perClass[classIndex]/self.totaL
            return 0
        else:
            if Utils.gr(self.m_perBag[intIndex], 0):
                return self.m_perClassPerBag[intIndex][classIndex]/self.m_perBag[intIndex]
            return self.prob(classIndex)

    def laplaceProb(self,classIndex:int,intIndex:int=None):
        if intIndex is None:
            return (self.m_perClass[classIndex]+1)/(self.totaL+len(self.m_perClass))
        else:
            if Utils.gr(self.m_perBag[intIndex], 0):
                return (self.m_perClassPerBag[intIndex][classIndex]+1)/(self.m_perBag[intIndex]+len(self.m_perClass))
            return self.laplaceProb(classIndex)

    def maxClass(self,index:int=None):
        maxCount=0
        maxIndex=0
        if index is None:
            for i in range(len(self.m_perClass)):
                if Utils.gr(self.m_perClass[i], maxCount):
                    maxCount=self.m_perClass[i]
                    maxIndex=i
            return maxIndex
        else:
            if Utils.gr(self.m_perBag[index], 0):
                for i in range(len(self.m_perClass)):
                    if Utils.gr(self.m_perClassPerBag[index][i], maxCount):
                        maxCount=self.m_perClassPerBag[index][i]
                        maxIndex=i
                return maxIndex
            return self.maxClass()

    def perBag(self,bagIndex:int):
        return self.m_perBag[bagIndex]

    def perClass(self,classIndex:int):
        return self.m_perClass[classIndex]

    def numCorrect(self,index:int=None):
        if index is None:
            return self.m_perClass[self.maxClass()]
        return self.m_perClassPerBag[index][self.maxClass(index)]

    def numIncorrect(self,index:int=None):
        if index is None:
            return self.totaL-self.numCorrect()
        return self.m_perBag[index]-self.numCorrect(index)

    def numClasses(self):
        return len(self.m_perClass)

    def numBags(self):
        return len(self.m_perBag)

    def total(self):
        return self.totaL