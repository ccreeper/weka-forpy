from Instances import Instances
from typing import *
import copy

class SparseInstance():
    def __init__(self,weight:float,attValues:List[float],indices:List[int],maxNumValues:int):
        vals=0
        self.m_AttValues=[0.0]*len(attValues)
        self.m_Indices=[0]*len(indices)     #type:List[int]
        for i in range(len(attValues)):
            if attValues[i]!=0:
                self.m_AttValues[vals]=attValues[i]
                self.m_Indices[vals]=indices[i]
                vals+=1

        if vals != len(attValues):
            newVals=copy.deepcopy(self.m_AttValues[:vals])
            newIndices=copy.deepcopy(self.m_Indices[:vals])
            self.m_Indices=newIndices
            self.m_AttValues=newVals
        self.m_Weight=weight
        self.m_NumAttributes=maxNumValues
        self.m_Dataset=None

    def numAttributes(self):
        return self.m_NumAttributes

    def numValues(self):
        return len(self.m_Indices)

    def locateIndex(self,index:int):
        min=0
        max=len(self.m_Indices)-1
        if max == -1:
            return -1
        while self.m_Indices[min]<=index and self.m_Indices[max]>=index:
            current=(max+min)//2
            if self.m_Indices[current]>index:
                max=current-1
            elif self.m_Indices[current]<index:
                min=current+1
            else:
                return current
        if self.m_Indices[max]<index:
            return max
        else:
            return min-1

    def value(self,attrIndex:int):
        index=self.locateIndex(attrIndex)
        if index>=0 and self.m_Indices[index]==attrIndex:
            return self.m_AttValues[index]
        else:
            return 0

    def valueSparse(self,index:int):
        return self.m_AttValues[index]

    def positionIndex(self,pos:int):
        return self.m_Indices[pos]