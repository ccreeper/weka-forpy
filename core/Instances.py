
from Attributes import Attribute
from AttributeStats import AttributeStats
from Stats import Stats
from Utils import Utils
from typing import *
from copy import *

class Instance():
    def __init__(self,data:List):
        self.m_Data=data

    def setDataset(self,inst:'Instances'):
        self.m_Dataset=inst

    def value(self,index:int):
        return self.m_Data[index]

    def isMissing(self,attrIndex:int):
        return Utils.isMissingValue(self.m_Data[attrIndex])

    def weight(self):
        return 1

    def stringValue(self,index:int):
        return self.m_Dataset.attribute(index).value(self.value(index))

    def attribute(self,index:int)->Attribute:
        return self.m_Dataset.attribute(index)

    def setValue(self,index:int,value):
        self.m_Data[index]=value

    def deleteAttributeAt(self,pos:int):
        if pos >= 0 and pos < len(self.m_Data):
            self.m_Data.pop(pos)

    #insertAttributeAt

#TODO 将所有数据处理成float,衍生Instance类
class Instances(object):
    def __init__(self,data,capacity=None):
        self.index=0
        if isinstance(data,dict):
            self.m_RelationName=data.get("relation")
            self.m_Attributes=[]    #type:List[Attribute]
            self.m_Instances=[] #type:List[Instance]
            self.m_ClassIndex=-1
            self.m_NamesToAttributeIndices=None     #type:Dict
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
                self.add(self.createInstance(item))

            self.m_NamesToAttributeIndices=dict()
            for i in range(self.numAttributes()):
                self.attribute(i).setIndex(i)
                self.m_NamesToAttributeIndices.update({self.attribute(i).name():i})

        if isinstance(data,Instances):
            if capacity is None:
                capacity=data.numInstances()
            self.initialize(data,capacity)
            data.copyInstances(0,data.numInstances(),self)

    def initialize(self,dataset,capacity:int):
        if capacity<0:
            capacity=0
        self.m_ClassIndex=dataset.m_ClassIndex
        self.m_RelationName=dataset.m_RelationName
        self.m_Attributes=dataset.m_Attributes
        self.m_Instances=[]
        self.m_NamesToAttributeIndices=dataset.m_NamesToAttributeIndices

    def setClassIndex(self,classIndex:int):
        self.m_ClassIndex=classIndex

    def classIndex(self):
        return self.m_ClassIndex

    def numInstances(self):
        return len(self.m_Instances)

    def numAttributes(self):
        return len(self.m_Attributes)

    def instance(self,index:int)->Instance:
        return self.m_Instances[index]

    #权重涉及到稀疏数据的流处理，故不做打算，默认权重为1.0
    def sumOfWeight(self):
        return len(self.m_Instances)

    @overload
    def attribute(self,index:int)->Attribute:...
    @overload
    def attribute(self,name:str)->Attribute:...

    def attribute(self,a0)->Attribute:
        if isinstance(a0,int):
            return self.m_Attributes[a0]
        elif isinstance(a0,str):
            index=self.m_NamesToAttributeIndices.get(a0)
            if index is None:
                return None
            return self.m_Attributes[index]
        return None

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

    def createInstance(self,data:List)->Instance:
        result=[]
        for i in range(self.numAttributes()):
            if data[i] is None:
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


    def stringFreeStructure(self):
        newAtts=[]
        for att in self.m_Attributes:
            if att.type() == Attribute.STRING:
                newAtts.append(Attribute(att.name(),None,att.index()))
        if len(newAtts) == 0:
            return Instances(self,0)
        atts=deepcopy(self.m_Attributes)
        for att in newAtts:
            atts[att.index()]=att
        result=Instances(self,0)
        result.m_Attributes=atts
        return result

    def insertAttributeAt(self,att:Attribute,pos:int):
        att.setIndex(pos)
        newList=[None]*(len(self.m_Attributes)+1)
        newMap=dict()
        for i in range(pos):
            oldAtt=self.m_Attributes[i]
            newList.append(oldAtt)
            newMap.update({oldAtt.name(),i})
        newList.append(att)
        newMap.update({att.name(),pos})
        for i in range(len(self.m_Attributes)):
            newAtt=self.m_Attributes[i]
            newAtt.setIndex(i+1)
            newList.append(newAtt)
            newMap.update({newAtt.name(),i+1})
        self.m_Attributes=newList
        self.m_NamesToAttributeIndices=newMap
        if self.m_ClassIndex >= pos:
            self.m_ClassIndex+=1

    def relationName(self):
        return self.m_RelationName

    def setRelationName(self,name:str):
        self.m_RelationName=name

    def delete(self,index:int):
        self.m_Instances.pop(index)

    def add(self,inst:Instance,index:int=-1):
        newInstance=copy(inst)
        newInstance.setDataset(self)
        if index <0:
            self.m_Instances.append(newInstance)
        else:
            self.m_Instances.insert(index,newInstance)

    def copyInstances(self,fromIndex:int,num:int,dest:'Instances'):
        for i in range(num):
            dest.add(self.instance(fromIndex+i))

    def renameAttribute(self,attIndex:int,name:str)->bool:
        existingAtt=self.attribute(name)
        if existingAtt is not None:
            return False
        newAtt=self.attribute(attIndex).copy(name)
        self.m_NamesToAttributeIndices.pop(self.attribute(attIndex).name())
        self.m_NamesToAttributeIndices.update({newAtt.name():attIndex})
        self.m_Attributes.pop(attIndex)
        self.m_Attributes.insert(attIndex,newAtt)
        return True

    def deleteAttributeAt(self,position:int):
        if position<0 or position>=self.numAttributes():
            return
        if position == self.m_ClassIndex:
            return
        for i in range(position+1,self.numAttributes()):
            attr=self.attribute(i)
            attr.setIndex(i-1)
            self.m_NamesToAttributeIndices.update({attr.name():i-1})
        self.m_NamesToAttributeIndices.pop(self.attribute(position).name())
        self.m_Attributes.pop(position)
        if self.m_ClassIndex > position:
            self.m_ClassIndex-=1

        for i in range(self.numInstances()):
            self.instance(i).deleteAttributeAt(position)
