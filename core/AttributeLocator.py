from typing import *
from Instances import Instances,Instance
from Attributes import Attribute
import copy

class AttributeLocator():
    def __init__(self,data:Instances,type:int,a0=None,a1=None):
        self.m_AllowedIndices=None  #type:List[int]
        self.m_Attributes=None      #type:List[bool]
        self.m_Locators=None        #type:List[AttributeLocator]
        self.m_Type=-1
        self.m_Data=None        #type:Instances
        self.m_Indices=None     #type:List[int]
        self.m_LocatorIndices=None  #type:List[int]
        if a0 is None and a1 is None:
            self.__init__(data,type,0,data.numAttributes()-1)
        elif isinstance(a0,int) and isinstance(a1,int):
            indices=[]
            for i in range(a1-a0+1):
                indices.append(a0+i)
            self.initialize(data,type,indices)
        elif isinstance(a0,List) and a1 is None:
            self.initialize(data,type,a0)


    def initialize(self,data:Instances,type:int,indices:List[int]):
        self.m_Data=Instances(data,0)
        self.m_Type=type
        self.m_AllowedIndices=copy.deepcopy(indices)
        self.locate()
        self.m_Indices=self.find(True)
        self.m_LocatorIndices=self.find(False)

    def find(self,findAttrs:bool):
        indices=[]
        if findAttrs:
            for i in range(len(self.m_Attributes)):
                if self.m_Attributes[i]:
                    indices.append(i)
        else:
            for i in range(len(self.m_Locators)):
                if self.m_Locators[i]!=None:
                    indices.append(i)
        result=[]
        for i in range(len(indices)):
            result.append(indices[i])
        return result

    def locate(self):
        self.m_Attributes=[]
        self.m_Locators=[None]*len(self.m_AllowedIndices)
        for i in range(len(self.m_AllowedIndices)):
            self.m_Attributes.append(self.m_Data.attribute(self.m_AllowedIndices[i]).type() == self.getType())

    def getType(self):
        return self.m_Type
