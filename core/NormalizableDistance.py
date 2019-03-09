from Range import Range
from typing import *
from Instances import Instances,Instance
from Attributes import Attribute
from core.neighboursearch.PerformanceStats import PerformanceStats
from Utils import Utils

class NormalizableDistance():
    R_MIN=0
    R_MAX=1
    R_WIDTH=2
    def __init__(self,data:Instances=None):
        self.m_AttributeIndices=Range("first-last")
        self.m_DontNormalize=False
        self.m_Ranges=None      #type:List[List]
        self.m_ActiveIndices=None       #type:List
        if data is None:
            self.invalidate()
        else:
            self.setInstances(data)

    def invalidate(self):
        self.m_Validated = False


    def setInstances(self,inst:Instances):
        self.m_Data=inst
        self.invalidate()

    def clean(self):
        self.m_Data=Instances(self.m_Data,0)

    def update(self,ins:Instance):
        self.validate()
        self.m_Ranges=self.updateRanges(ins,self.m_Ranges)

    @overload
    def distance(self,first:Instance,second:Instance):...
    @overload
    def distance(self,first:Instance,second:Instance,stats:PerformanceStats):...
    @overload
    def distance(self,first:Instance,second:Instance,cutOffValue:float):...
    @overload
    def distance(self,first:Instance,second:Instance,cutOffValue:float,stats:PerformanceStats):...

    def distance(self, first: Instance, second: Instance,a0=None,a1=None):
        if a0 is None or isinstance(a0,PerformanceStats):
            return self.distance(first,second,float("inf"),a0)
        elif isinstance(a0,float):
            distance=0
            firstNumValues=first.numValues()
            secondNumValues=second.numValues()
            numAttributes=self.m_Data.numAttributes()
            classIndex=self.m_Data.classIndex()
            self.validate()
            p1=p2=0
            while p1<firstNumValues or p2<secondNumValues:
                if p1>=firstNumValues:
                    firstI=numAttributes
                else:
                    firstI=first.index(p1)
                if p2>=secondNumValues:
                    secondI=numAttributes
                else:
                    secondI=second.index(p2)
                if firstI == classIndex:
                    p1+=1
                    continue
                if firstI<numAttributes and not self.m_ActiveIndices[firstI]:
                    p1+=1
                    continue
                if secondI == classIndex:
                    p2+=1
                    continue
                if secondI<numAttributes and not self.m_ActiveIndices[secondI]:
                    p2+=1
                    continue
                if firstI == secondI:
                    diff=self.difference(firstI,first.valueSparse(p1),second.valueSparse(p2))
                    p1+=1
                    p2+=1
                elif firstI>secondI:
                    diff=self.difference(secondI,0,second.valueSparse(p2))
                else:
                    diff=self.difference(firstI,first.valueSparse(p1),0)
                    p1+=1
                if isinstance(a1,PerformanceStats):
                    a1.incrPointCount()
                distance=self.updateDistance(distance,diff)
                if distance>a0:
                    return float('inf')
            return distance

    def updateDistance(self,currDist:float,diff:float)->float:...

    def difference(self,index:int,val1:float,val2:float):
        if self.m_Data.attribute(index).type() == Attribute.NOMINAL:
            if Utils.isMissingValue(val1) or Utils.isMissingValue(val2) or int(val1)!=int(val2):
                return 1
            return 0
        elif self.m_Data.attribute(index).type() == Attribute.NUMERIC:
            if Utils.isMissingValue(val1) or Utils.isMissingValue(val2):
                if Utils.isMissingValue(val1) and Utils.isMissingValue(val2):
                    if not self.m_DontNormalize:
                        return 1
                    return self.m_Ranges[index][self.R_WIDTH]
                else:
                    if Utils.isMissingValue(val2):
                        diff=self.norm(val1,index) if not self.m_DontNormalize else val1
                    else:
                        diff=self.norm(val2,index) if not self.m_DontNormalize else val2
                    if not self.m_DontNormalize and diff<0.5:
                        diff=1-diff
                    elif self.m_DontNormalize:
                        if (self.m_Ranges[index][self.R_MAX]-diff) > (diff-self.m_Ranges[index][self.R_MIN]):
                            return self.m_Ranges[index][self.R_MAX]-diff
                        else:
                            return diff-self.m_Ranges[index][self.R_MIN]
                    return diff
            else:
                return (self.norm(val1,index)-self.norm(val2,index)) if not self.m_DontNormalize else (val1-val2)
        else:
            return 0

    def norm(self,x:float,i:int):
        if self.m_Ranges[i][self.R_WIDTH]==0:
            return 0
        return (x-self.m_Ranges[i][self.R_MIN])/self.m_Ranges[i][self.R_WIDTH]

    def validate(self):
        if not self.m_Validated:
            self.initialize()
            self.m_Validated=True

    def initialize(self):
        self.initializeAttributeIndices()
        self.initializeRanges()

    def initializeAttributeIndices(self):
        self.m_AttributeIndices.setUpper(self.m_Data.numAttributes()-1)
        self.m_ActiveIndices=[]
        for i in range(self.m_Data.numAttributes()):
            self.m_ActiveIndices.append(self.m_AttributeIndices.isInRange(i))

    def initializeRanges(self)->List[List]:
        if self.m_Data is None:
            self.m_Ranges=None
            return self.m_Ranges
        numAtt=self.m_Data.numAttributes()
        ranges=[[0]*3 for i in range(numAtt)]
        if self.m_Data.numInstances() <= 0:
            self.initializeRangesEmpty(numAtt,ranges)
            self.m_Ranges=ranges
            return self.m_Ranges
        else:
            self.updateRangesFirst(self.m_Data.instance(0),numAtt,ranges)
        for i in range(self.m_Data.numInstances()):
            self.updateRanges(self.m_Data.instance(i),ranges)
        self.m_Ranges=ranges
        return self.m_Ranges


    def initializeRangesEmpty(self,numAtt:int,ranges:List[List]):
        for j in range(numAtt):
            ranges[j][self.R_MIN]=float('inf')
            ranges[j][self.R_MAX]=float('inf')
            ranges[j][self.R_WIDTH]=float('inf')

    def updateRangesFirst(self,instance:Instance,numAtt:int,ranges:List[List]):
        for i in range(len(ranges)):
            for j in range(len(ranges[i])):
                ranges[i][j]=0
        numVals=instance.numValues()
        for j in range(numVals):
            currIndex=instance.index(j)
            if not instance.isMissingSparse(j):
                return True
        return False

    def updateRanges(self,instance:Instance,ranges:List[List[float]]):
        numVals=instance.numValues()
        prevIndex=0
        for j in range(numVals):
            currIndex=instance.index(j)
            while prevIndex < currIndex:
                if 0<ranges[prevIndex][self.R_MIN]:
                    ranges[prevIndex][self.R_MIN]=0
                    ranges[prevIndex][self.R_WIDTH]=ranges[prevIndex][self.R_MAX]-ranges[prevIndex][self.R_MIN]
                if 0>ranges[prevIndex][self.R_MAX]:
                    ranges[prevIndex][self.R_MAX]=0
                    ranges[prevIndex][self.R_WIDTH]=ranges[prevIndex][self.R_MAX]-ranges[prevIndex][self.R_MIN]
                prevIndex+=1
            prevIndex+=1
            if not instance.isMissingSparse(j):
                val=instance.valueSparse(j)
                if val < ranges[currIndex][self.R_MIN]:
                    ranges[currIndex][self.R_MIN]=val
                    ranges[currIndex][self.R_WIDTH]=ranges[currIndex][self.R_MAX]-ranges[currIndex][self.R_MIN]
                if val > ranges[currIndex][self.R_MAX]:
                    ranges[currIndex][self.R_MAX]=val
                    ranges[currIndex][self.R_WIDTH]=ranges[currIndex][self.R_MAX]-ranges[currIndex][self.R_MIN]
        return ranges