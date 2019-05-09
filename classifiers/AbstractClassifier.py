from typing import *

from core.Attributes import Attribute
from core.Capabilities import Capabilities
from core.Instances import Instance

from classifiers.Classifier import Classifier
from core.Utils import Utils
from core.CapabilitiesHandler import CapabilitiesHandler


class AbstractClassifier(Classifier,CapabilitiesHandler):
    NUM_DECIMAL_PLACES_DEFAULT=2
    BATCH_SIZE_DEFAULT="100"
    propertyList={'numDecimalPlaces':'2','doNotCheckCapabilities':'False','batchSize':'100'}
    methodList={"numDecimalPlaces":"setNumDecimalPlaces","doNotCheckCapabilities":"setDoNotCheckCapabilities",
                "batchSize":"setBatchSize"}
    def __init__(self):
        self.numDecimalPlaces=self.NUM_DECIMAL_PLACES_DEFAULT
        self.batchSize=self.BATCH_SIZE_DEFAULT
        self.doNotCheckCapabilities=False

    def distributionForInstance(self,instance:Instance)->List[float]:
        dist=[0]*instance.numClasses()
        if instance.classAttribute().type() == Attribute.NOMINAL:
            classification=self.classifyInstance(instance)
            if Utils.isMissingValue(classification):
                return dist
            else:
                dist[int(classification)]=1.0
            return dist
        elif instance.classAttribute().type() == Attribute.NUMERIC or instance.classAttribute().type() == Attribute.DATE:
            dist[0]=self.classifyInstance(instance)
            return dist
        return dist

    def classifyInstance(self,instance:Instance):
        dist=self.distributionForInstance(instance)
        if dist is None:
            raise Exception("Null distribution predicted")
        if instance.classAttribute().type() == Attribute.NOMINAL:
            max=maxIndex=0
            for i in range(len(dist)):
                if dist[i]>max:
                    maxIndex=i
                    max=dist[i]
            if max > 0:
                return maxIndex
            return Utils.missingValue()
        elif instance.classAttribute().type() == Attribute.NUMERIC or instance.classAttribute().type() == Attribute.DATE:
            return dist[0]
        return Utils.missingValue()


    def getCapabilities(self):
        result=Capabilities(self)
        result.enableAll()
        return result

    def setNumDecimalPlaces(self,value:str):
        try:
            val=int(value)
            self.numDecimalPlaces=val
            self.propertyList.update({"numDecimalPlaces":value})
        except ValueError:
            pass

    def setDoNotCheckCapabilities(self,value:int):
        if value == 0:
            self.doNotCheckCapabilities=False
        else:
            self.doNotCheckCapabilities=True

    def setBatchSize(self,value:str):
        try:
            val=int(value)
            self.batchSize=val
            self.propertyList.update({"batchSize":value})
        except ValueError:
            pass


    @classmethod
    def getAllMethods(cls):
        return cls.methodList

    @classmethod
    def getAllProperties(cls):
        return cls.propertyList

