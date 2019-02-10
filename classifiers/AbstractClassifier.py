from classifiers.Classifier import Classifier
from core.CapabilitiesHandler import CapabilitiesHandler
from core.Capabilities import Capabilities
from typing import *

class AbstractClassifier(Classifier,CapabilitiesHandler):
    NUM_DECIMAL_PLACES_DEFAULT=2
    BATCH_SIZE_DEFAULT="100"
    propertyList=['numDecimalPlaces','doNotCheckCapabilities','batchSize']
    methodList=[]
    def __init__(self):
        self.numDecimalPlaces=self.NUM_DECIMAL_PLACES_DEFAULT
        self.batchSize=self.BATCH_SIZE_DEFAULT
        self.doNotCheckCapabilities=False


    def getCapabilities(self):
        result=Capabilities(self)
        result.enableAll()
        return result

    @classmethod
    def getAllMethods(cls):
        return cls.methodList

    @classmethod
    def getAllProperties(cls):
        return cls.propertyList

