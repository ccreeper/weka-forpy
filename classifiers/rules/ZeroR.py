from classifiers.Classifier import Classifier
from classifiers.AbstractClassifier import AbstractClassifier
from Capabilities import Capabilities
from Attributes import Attribute

class ZeroR(AbstractClassifier):
    def __init__(self):
        super().__init__()
        self.m_ClassValue=0
        self.m_Counts=[]
        self.m_Class=None   #type:Attribute

    def getCapabilities(self)->Capabilities:
        result=