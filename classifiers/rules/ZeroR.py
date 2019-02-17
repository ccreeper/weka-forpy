from classifiers.Classifier import Classifier
from classifiers.AbstractClassifier import AbstractClassifier
from Capabilities import Capabilities,CapabilityEnum
from Attributes import Attribute
from Instances import Instances,Instance
from Utils import Utils
from typing import *


class ZeroR(AbstractClassifier):
    def __init__(self):
        super().__init__()
        self.m_ClassValue=0
        self.m_Counts=None  #ype:List
        self.m_Class=None   #type:Attribute

    def __str__(self):
        if self.m_Class is None:
            return "ZeroR: No model built yet."
        if self.m_Counts is None:
            return "ZeroR predicts class value: " + str(self.m_ClassValue)
        return "ZeroR predicts class value: " + self.m_Class.value(int(self.m_ClassValue))

    def addPropertiesToList(self):
        pass

    def addMethodsToList(self):
        pass

    def getCapabilities(self)->Capabilities:
        result=super().getCapabilities()
        result.disableAll()

        result.enable(CapabilityEnum.NOMINAL_ATTRIBUTES)
        result.enable(CapabilityEnum.NUMERIC_ATTRIBUTES)
        result.enable(CapabilityEnum.DATE_ATTRIBUTES)
        result.enable(CapabilityEnum.STRING_ATTRIBUTES)
        result.enable(CapabilityEnum.RELATIONAL_ATTRIBUTES)
        result.enable(CapabilityEnum.MISSING_VALUES)

        result.enable(CapabilityEnum.NOMINAL_CLASS)
        result.enable(CapabilityEnum.NUMERIC_CLASS)
        result.enable(CapabilityEnum.DATE_CLASS)
        result.enable(CapabilityEnum.MISSING_CLASS_VALUES)

        result.setMinimumNumberInstances(0)
        return result

    def buildClassifier(self,instances:Instances):
        self.getCapabilities().testWithFail(instances)
        sumOfWeights=0
        self.m_Class=instances.classAttribute()
        self.m_ClassValue=0
        attrType=instances.classAttribute().type()
        if attrType == Attribute.NUMERIC:
            self.m_Counts=None
        elif attrType == Attribute.NOMINAL:
            self.m_Counts=[]
            for i in range(instances.numClasses()):
                self.m_Counts.append(1)
            sumOfWeights=instances.numClasses()
        for instance in instances:
            classValue=instance.classValue()
            if not Utils.isMissingValue(classValue):
                if instances.classAttribute().isNominal():
                    self.m_Counts[classValue]+=instance.weight()
                else:
                    self.m_ClassValue+=instance.weight()*classValue
                sumOfWeights+=instance.weight()
        if instances.classAttribute().isNumeric():
            if Utils.gr(sumOfWeights,0):
                self.m_ClassValue/=sumOfWeights
        else:
            self.m_ClassValue=Utils.maxIndex(self.m_Counts)
            Utils.normalize(self.m_Counts,sumOfWeights)

    def classifyInstance(self,instance:Instance):
        return self.m_ClassValue

    def distributionForInstance(self,instance:Instance):
        if self.m_Counts is None:
            result=[0]
            result[0]=self.m_ClassValue
            return result
        else:
            return self.m_Counts[:]