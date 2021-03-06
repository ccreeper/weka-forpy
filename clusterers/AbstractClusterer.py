from core.Capabilities import Capabilities
from core.Instances import Instance

from clusterers.Clusterer import Clusterer
from core.Utils import Utils


class AbstractClusterer(Clusterer):
    propertyList = ['doNotCheckCapabilities']
    methodList = []
    def __init__(self):
        self.doNotCheckCapabilities=False

    def clusterInstance(self,instance:Instance):
        dist=self.distributionForInstance(instance)
        if dict is None:
            raise Exception("Null distribution predicted")
        if sum(dist) <= 0:
            raise Exception("Unable to cluster instance")
        return Utils.maxIndex(dist)

    def distributionForInstance(self,instance:Instance):
        d=[0]*self.numberOfClusters()
        d[self.clusterInstance(instance)]=1
        return d

    def setDoNotCheckCapabilities(self,flag:bool):
        self.doNotCheckCapabilities=flag

    def getDoNotCheckCapabilities(self):
        return self.doNotCheckCapabilities

    def getCapabilities(self)->Capabilities:
        result=Capabilities(self)
        result.enableAll()
        return result

    @classmethod
    def getAllMethods(cls):
        return cls.methodList

    @classmethod
    def getAllProperties(cls):
        return cls.propertyList
