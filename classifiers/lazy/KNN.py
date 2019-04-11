from typing import *
from classifiers.AbstractClassifier import AbstractClassifier
from classifiers.rules.ZeroR import ZeroR
from Attributes import Attribute
from Capabilities import Capabilities,CapabilityEnum
from Instances import Instances,Instance
from Utils import Utils
from core.neighboursearch.LinearNNSearch import LinearNNSearch
from Tag import Tag
import math

#默认距离权重为0，不使用交叉验证
class KNN(AbstractClassifier):
    WEIGHT_NONE=0
    WEIGHT_INVERSE=1
    WEIGHT_SIMILARITY=2
    TAGS_WEIGHTING=[Tag(WEIGHT_NONE,"No distance weighting"),
                    Tag(WEIGHT_INVERSE,"Weight by 1/distance"),
                    Tag(WEIGHT_SIMILARITY,"Weight by 1-distance")]
    propertyList={"kNN":"1","DistanceWeighting":"TAGS_WEIGHTING"}
    methodList = {"kNN":"setkNN","DistanceWeighting":"setDistanceWeighting"}
    def __init__(self,k:int=None):
        super().__init__()
        self.m_NNSearch=LinearNNSearch()
        self.m_Train=None   #type:Instances
        self.initilize()
        if k is not None:
            self.setKNN(k)

    def __str__(self):
        if self.m_Train is None:
            return "IBk: No model built yet."
        if self.m_Train.numInstances() == 0:
            return "Warning: no training instances - ZeroR model used."
        #TODO 高级
        result="IB1 instance-based classifier\n" +"using " + str(self.kNN)
        if self.DistanceWeighting == self.WEIGHT_INVERSE:
            result+=" inverse-distance-weighted"
        elif self.DistanceWeighting == self.WEIGHT_SIMILARITY:
            result+= " similarity-weighted"
        result+=" nearest neighbour(s) for classification\n"
        if self.WindowSize != 0:
            result+="using a maximum of " + str(self.WindowSize) + " (windowed) training instances\n"
        return result

    def setkNN(self,value:str):
        try:
            val=int(value)
            self.kNN=val
            self.propertyList.update({"kNN":value})
        except ValueError:
            pass

    def setDistanceWeighting(self,value:int):
        self.DistanceWeighting=self.TAGS_WEIGHTING[value].getID()


    def initilize(self):
        self.setKNN(1)
        #多少个样本用于分类，默认整个样本集
        self.WindowSize=0
        self.DistanceWeighting=self.WEIGHT_NONE
        self.CrossValidate=False
        self.MEanSquared=False

    def setKNN(self,k:int):
        self.kNN=k
        self.m_kNNUpper=k
        self.m_kNNValid=False

    def getKNN(self):
        return self.kNN

    def getCapabilities(self):
        result=super().getCapabilities()
        result.disableAll()

        result.enable(CapabilityEnum.NOMINAL_ATTRIBUTES)
        result.enable(CapabilityEnum.NUMERIC_ATTRIBUTES)
        result.enable(CapabilityEnum.DATE_ATTRIBUTES)
        result.enable(CapabilityEnum.MISSING_VALUES)

        result.enable(CapabilityEnum.NOMINAL_CLASS)
        result.enable(CapabilityEnum.NUMERIC_CLASS)
        result.enable(CapabilityEnum.DATE_CLASS)
        result.enable(CapabilityEnum.MISSING_CLASS_VALUES)

        result.setMinimumNumberInstances(0)
        return result

    def buildClassifier(self,data:Instances):
        self.getCapabilities().testWithFail(data)
        instances=Instances(data)
        instances.deleteWithMissingClass()

        self.m_NumClasses=instances.numClasses()
        self.m_ClassType=instances.classAttribute().type()
        self.m_Train=Instances(instances,0,instances.numInstances())
        #只保存了样本集
        if self.WindowSize > 0 and instances.numInstances() > self.WindowSize:
            self.m_Train=Instances(self.m_Train,self.m_Train.numInstances()-self.WindowSize,self.WindowSize)
        self.m_NumAttributesUsed=0
        for i in range(self.m_Train.numAttributes()):
            if i != self.m_Train.classIndex() and (self.m_Train.attribute(i).isNominal() or  self.m_Train.attribute(i).isNumeric()):
                self.m_NumAttributesUsed+=1
        self.m_NNSearch.setInstances(self.m_Train)
        self.m_kNNValid=False
        self.m_defaultModel=ZeroR()
        self.m_defaultModel.buildClassifier(instances)


    def distributionForInstance(self,instance:Instance)->List[float]:
        if self.m_Train.numInstances() == 0:
            return self.m_defaultModel.distributionForInstance(instance)
        #超过样本容量，则循环删除
        if self.WindowSize > 0 and self.m_Train.numInstances() > self.WindowSize:
            self.m_kNNValid=False
            deletedInstance=False
            while(self.m_Train.numInstances()>self.WindowSize):
                self.m_Train.delete(0)
            if deletedInstance is True:
                self.m_NNSearch.setInstances(self.m_Train)
        if not self.m_kNNValid and self.CrossValidate and self.m_kNNUpper>=1:
            pass
        self.m_NNSearch.addInstanceInfo(instance)
        #获取k个邻居的样本集和距离
        neighbours=self.m_NNSearch.kNearestNeighbours(instance,self.kNN)
        distances=self.m_NNSearch.getDistances()
        distribution=self.makeDistribution(neighbours,distances)
        return distribution

    #获取k个邻近样本的概率分布
    def makeDistribution(self,neighbours:Instances,distances:List)->List[float]:
        distribution=[0]*self.m_NumClasses
        total=0
        if self.m_ClassType == Attribute.NOMINAL:
            for i in range(self.m_NumClasses):
                distribution[i]=1/max(1,self.m_Train.numInstances())
            total=self.m_NumClasses/max(1,self.m_Train.numInstances())
        for i in range(neighbours.numInstances()):
            current=neighbours.instance(i)
            distances[i]=distances[i]*distances[i]
            distances[i]=math.sqrt(distances[i]/self.m_NumAttributesUsed)
            if self.DistanceWeighting == self.WEIGHT_INVERSE:
                weight=1/distances[i]
            elif self.DistanceWeighting == self.WEIGHT_SIMILARITY:
                weight=1-distances[i]
            else:
                weight=1
            weight*=current.weight()
            if self.m_ClassType == Attribute.NOMINAL:
                distribution[int(current.classValue())]+=weight
            elif self.m_ClassType == Attribute.NUMERIC:
                distribution[0]+=current.classValue()*weight
            total+=weight
        if total > 0:
            Utils.normalize(distribution,total)
        return distribution