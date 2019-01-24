
from Attributes import Attribute
from AttributeStats import AttributeStats
from Stats import Stats
from Utils import Utils
from typing import *

class Instance():
    def __init__(self,data:List):
        self.m_Data=data

    def value(self,index:int):
        return self.m_Data[index]

    def isMissing(self,attrIndex:int):
        return Utils.isMissingValue(self.m_Data[attrIndex])

    def weight(self):
        return 1

#TODO 将所有数据处理成float,衍生Instance类
class Instances(object):
    def __init__(self,data):
        self.index=0
        if isinstance(data,dict):
            self.m_RelationName=data.get("relation")
            self.m_Attributes=[]
            self.m_Instances=[] #type:List[Instance]
            for attr in data.get("attributes"):
                second=attr[1]
                attribute=None
                if isinstance(second,str):
                    if second.lower()=="numeric" or second.lower()=="real":
                        attribute=Attribute(attr[0])
                    else:
                        attribute=Attribute(attr[0],True)
                else:
                    attribute=Attribute(attr[0],attr[1])
                self.m_Attributes.append(attribute)

            for item in data.get("data"):
                self.m_Instances.append(self.loadInstance(item))

    def numInstances(self):
        return len(self.m_Instances)

    def numAttributes(self):
        return len(self.m_Attributes)

    def instance(self,index:int)->Instance:
        return self.m_Instances[index]

    #权重涉及到稀疏数据的流处理，故不做打算，默认权重为1.0
    def sumOfWeight(self):
        return len(self.m_Instances)

    def attribute(self,index)->Attribute:
        return self.m_Attributes[index]

    def attributeStats(self,index:int)->AttributeStats:
        result=AttributeStats()
        if self.attribute(index).isNominal():
            result.nominalCounts=[0]*self.attribute(index).numValues()
            result.nominalWeights=[0]*self.attribute(index).numValues()
        if self.attribute(index).isNumeric():
            result.numericStats=Stats()
        result.totalCount=self.numInstances()
        map=dict()
        for current in self.m_Instances:
            key=current.value(index)
            if Utils.isMissingValue(key):
                result.missingCount+=1
            else:
                values=map.get(key)
                if values is None:
                    values=[1.0,1.0]
                    map[key]=values
                else:
                    values[0]+=1.0
                    #values[1]=values[1]+current.weight()
                    values[1]+=1.0

        for key,val in map.items():
            result.addDistinct(key,val[0],val[1])
        return result

    def loadInstance(self,data:List)->Instance:
        result=[]
        for i in range(self.numAttributes()):
            if data[i] == '?':
                result.append(Utils.missingValue())
            else:
                if self.attribute(i).type() == Attribute.NOMINAL:
                    value=self.attribute(i).indexOfValue(data[i])
                elif self.attribute(i).type() == Attribute.NUMERIC:
                    value=data[i]
                elif self.attribute(i).type() == Attribute.STRING:
                    value=self.attribute(i).addStringValue(data[i])
                result.append(value)

        inst=Instance(result)
        return inst

    def sort(self,attrIndex:int):
        if not self.attribute(attrIndex).isNominal():
            vals=[0.0]*self.numInstances()
            backup=[None]*self.numInstances()     #type:List[Instance]

            for i in range(len(vals)):
                inst=self.instance(i)
                backup[i]=inst
                val=inst.value(attrIndex)
                if Utils.isMissingValue(val):
                    vals[i]=float('inf')
                else:
                    vals[i]=val

            sortOrder=Utils.sortWithNoMissingValues(vals)
            for i in range(len(vals)):
                self.m_Instances[i]=backup[sortOrder[i]]
        else:
            self.sortBasedOnNominalAttribute(attrIndex)


    def sortBasedOnNominalAttribute(self,attrIndex:int):
        counts=[0]*self.attribute(attrIndex).numValues()
        backup=[None]*self.numInstances()       #type:List[Instance]
        j=0
        for inst in self.m_Instances:
            backup[j]=inst
            j+=1
            if not inst.isMissing(attrIndex):
                counts[int(inst.value(attrIndex))]+=1

        indices=[0]*len(counts)
        start=0
        for i in range(len(counts)):
            indices[i]=start
            start+=counts[i]

        for inst in backup:
            if not inst.isMissing(attrIndex):
                self.m_Instances[indices[(int)(inst.value(attrIndex))]]=inst
                indices[(int)(inst.value(attrIndex))]+=1
            else:
                self.m_Instances[start]=inst
                start+=1
