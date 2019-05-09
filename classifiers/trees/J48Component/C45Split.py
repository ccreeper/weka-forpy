from core.Instances import Instances, Instance

from classifiers.trees.J48Component.ClassifierSplitModel import ClassifierSplitModel
from classifiers.trees.J48Component.Distribution import Distribution
from core.Utils import Utils


class C45Split(ClassifierSplitModel):

    def __init__(self,attIndex:int,minNoObj:int,sumOfWeights:float,useMDLcorrection:bool):
        super().__init__()
        self.m_distribution=None    #type:Distribution
        self.m_numSubsets=0
        self.m_attIndex=attIndex
        self.m_minNoObj=minNoObj
        self.m_sumOfWeights=sumOfWeights
        self.m_useMDLcorrection=useMDLcorrection
        self.m_splitPoint=float("inf")
        self.m_infoGain=0
        self.m_gainRatio=0


    def buildClassifer(self,instances:Instances):
        self.m_numSubsets=0
        self.m_splitPoint=float("inf")
        self.m_infoGain=0
        self.m_gainRatio=0

        if instances.attribute(self.m_attIndex).isNominal():
            self.m_complexityIndex=instances.attribute(self.m_attIndex).numValues()
            self.m_index=self.m_complexityIndex
            self.handleEnumeratedAttribute(instances)
            print("att build after numSubsets:",self.numSubsets())
        else:
            self.m_complexityIndex=2
            self.m_index=0
            instances.sort(instances.attribute(self.m_attIndex))
            self.handleNumericAttribute(instances)
            print("num build after numSubsets:",self.numSubsets())


    def handleEnumeratedAttribute(self,instances:Instances):
        self.m_distribution=Distribution(self.m_complexityIndex,instances.numClasses())
        for inst in instances:
            if not inst.isMissing(self.m_attIndex):
                self.m_distribution.add(int(inst.value(self.m_attIndex)),inst)
        if self.m_distribution.check(self.m_minNoObj):
            self.m_numSubsets=self.m_complexityIndex
            self.m_infoGain=self.infoGainCrit.splitCritValue(self.m_distribution,self.m_sumOfWeights)
            self.m_gainRatio=self.gainRatioCrit.splitCritValue(self.m_distribution,self.m_sumOfWeights,self.m_infoGain)

    def handleNumericAttribute(self,trainInstances:Instances):
        next=1
        last=0
        splitIndex=-1
        self.m_distribution=Distribution(2,trainInstances.numClasses())
        i=0
        for inst in trainInstances:
            if inst.isMissing(self.m_attIndex):
                break
            self.m_distribution.add(1,inst)
            i+=1
        firstMiss=i
        minSplit=0.1*self.m_distribution.total()/trainInstances.numClasses()
        if Utils.gr(self.m_minNoObj, minSplit) or Utils.equal(minSplit, self.m_minNoObj):
            minSplit=self.m_minNoObj
        elif Utils.gr(minSplit, 25):
            minSplit=25
        if Utils.gr(2*minSplit, firstMiss):
            return
        defaultEnt=self.infoGainCrit.oldEnt(self.m_distribution)
        print("dfalut", defaultEnt)
        while next < firstMiss:
            if trainInstances.instance(next-1).value(self.m_attIndex)+1e-5 < trainInstances.instance(next).value(self.m_attIndex):
                self.m_distribution.shiftRange(1,0,trainInstances,last,next)
                if (Utils.gr(self.m_distribution.perBag(0), minSplit) or Utils.equal(self.m_distribution.perBag(0), minSplit))\
                        and (Utils.gr(self.m_distribution.perBag(1), minSplit) or Utils.equal(self.m_distribution.perBag(1), minSplit)):
                    currentInfoGain=self.infoGainCrit.splitCritValue(self.m_distribution,self.m_sumOfWeights,defaultEnt)
                    if Utils.gr(currentInfoGain, self.m_infoGain):
                        self.m_infoGain=currentInfoGain
                        splitIndex=next-1
                    self.m_index+=1
                last=next
            next+=1
        if self.m_index == 0:
            return
        if self.m_useMDLcorrection:
            self.m_infoGain=self.m_infoGain-(Utils.log2(self.m_index) / self.m_sumOfWeights)
        if Utils.gr(0, self.m_infoGain) or Utils.equal(0, self.m_infoGain):
            return
        self.m_numSubsets=2
        self.m_splitPoint=(trainInstances.instance(splitIndex+1).value(self.m_attIndex)
                          +trainInstances.instance(splitIndex).value(self.m_attIndex))/2
        if self.m_splitPoint == trainInstances.instance(splitIndex+1).value(self.m_attIndex):
            self.m_splitPoint=trainInstances.instance(splitIndex).value(self.m_attIndex)
        self.m_distribution=Distribution(2,trainInstances.numClasses())
        self.m_distribution.addRange(0,trainInstances,0,splitIndex+1)
        self.m_distribution.addRange(1,trainInstances,splitIndex+1,firstMiss)
        self.m_gainRatio=self.gainRatioCrit.splitCritValue(self.m_distribution,self.m_sumOfWeights,self.m_infoGain)


    def whichSubset(self,instance:Instance):
        if instance.isMissing(self.m_attIndex):
            return -1
        if instance.attribute(self.m_attIndex).isNominal():
            return int(instance.value(self.m_attIndex))
        elif instance.value(self.m_attIndex) <= self.m_splitPoint:
            return 0
        return 1


    def rightSide(self,index:int,data:Instances):
        text=""
        if data.attribute(self.m_attIndex).isNominal():
            text+=" = " + data.attribute(self.m_attIndex).value(index)
        elif index == 0:
            text+=" <= " + Utils.doubleToString(self.m_splitPoint, 6)
        else:
            text+=" > " + Utils.doubleToString(self.m_splitPoint, 6)
        return text

    def leftSide(self,data:Instances):
        return data.attribute(self.m_attIndex).name()

    def attIndex(self):
        return self.m_attIndex

    def splitPoint(self):
        return self.m_splitPoint

    def infoGain(self):
        return self.m_infoGain

    def gainRatio(self):
        return self.m_gainRatio

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

    def resetDistribution(self,data:Instances):
        insts=Instances(data,data.numInstances())
        for i in range(data.numInstances()):
            if self.whichSubset(data.instance(i)) > -1:
                insts.add(data.instance(i))
        newD=Distribution(insts,self)
        newD.addInstWithUnknown(data,self.m_attIndex)
        self.m_distribution=newD