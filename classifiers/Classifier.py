from Capabilities import Capabilities
from Instances import Instances,Instance
from typing import *

class Classifier():
    @classmethod
    def getAllProperties(cls):pass
    @classmethod
    def getAllMethods(cls):pass
    def buildClassifier(self,data:Instances):pass
    def getCapabilities(self)->Capabilities:pass
