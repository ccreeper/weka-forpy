from classifiers.Classifier import Classifier
from core.CapabilitiesHandler import CapabilitiesHandler
from core.Capabilities import Capabilities
from typing import *

class AbstractClassifier(Classifier,CapabilitiesHandler):
    NUM_DECIMAL_PLACES_DEFAULT=2
    BATCH_SIZE_DEFAULT="100"
    def __init__(self):
        self.m_numDecimalPlaces=self.NUM_DECIMAL_PLACES_DEFAULT
        self.m_BatchSize=self.BATCH_SIZE_DEFAULT

    def getCapabilities(self):
        result=Capabilities(self)
        result.enableAll()
        return result


