from AttributeLocator import AttributeLocator
from typing import *
from Instances import Instances,Instance
from Attributes import Attribute

class StringLocator(AttributeLocator):
    def __init__(self,data:Instances,a0=None,a1=None):
        if a0 is None and a1 is None:
            super().__init__(data,Attribute.STRING)
        elif isinstance(a0,int) and isinstance(a1,int):
            super().__init__(data,Attribute.STRING,a0,a1)
        elif isinstance(a0,List) and a1 is None:
            super().__init__(data,Attribute.STRING,a0)

    def getAttributeIndices(self):
        return self.m_Indices

    def getAllowedIndices(self):
        return self.m_AllowedIndices