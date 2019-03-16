
from typing import *
from Attributes import Attribute
from Stats import Stats
from Utils import Utils
from core.AttributeStats import AttributeStats
import copy
import random
import math

class Instance():
    def __init__(self,a0,a1=None):
        self.m_AttValues=[]
        if isinstance(a0, list) and a1 is None:
            self.m_AttValues=a0
            self.m_Weight=1
        elif isinstance(a0, Instance) and a1 is None:
            self.m_AttValues=a0.m_AttValues
            self.m_Weight=a0.weight()
            self.m_Dataset=None         #type:Instances
        elif isinstance(a0,float) and isinstance(a1,list):
            self.m_AttValues=a1
            self.m_Weight=a0
            self.m_Dataset=None
        elif isinstance(a0,int) and a1 is None:
            self.m_AttValues=[]
            for i in range(a0):
                self.m_AttValues.append(Utils.missingValue())
            self.m_Weight=1
            self.m_Dataset=None

    def __str__(self):
        return self.toStringMaxDecimalDigits(6)

    def toStringMaxDecimalDigits(self,afterDecimalPoint:int):
        text=self.toStringNoWeight(afterDecimalPoint)
        return text

    def insertAttributeAt(self,position:int):
        if self.m_Dataset is not None:
            raise Exception("Instance has accesss to a dataset!")
        if position < 0 or position > self.numAttributes():
            raise Exception("Can't insert attribute: index out of range")
        self.forceInsertAttributeAt(position)

    def forceInsertAttributeAt(self,position:int):
        newValues=self.m_AttValues[:]
        newValues.append(0)
        newValues[position]=Utils.missingValue()
        for i in range(position+1,len(self.m_AttValues)+1):
            newValues[i]=self.m_AttValues[i-1]
        self.m_AttValues=newValues

    def hasMissingValue(self):
        classIndex=self.classIndex()
        for i in range(self.numValues()):
            if self.index(i) != classIndex:
                if self.isMissingSparse(i):
                    return True
        return False

    def setWeight(self,weight:float):
        self.m_Weight=weight

    def numAttributes(self):
        return len(self.m_AttValues)

    def attributeSparse(self,indexOfIndex:int)->Attribute:
        return self.m_Dataset.attribute(self.index(indexOfIndex))

    def toStringNoWeight(self,afterDecimalPoint:int=None):
        text=""
        if afterDecimalPoint is None:
            return self.toStringNoWeight(6)
        for i in range(len(self.m_AttValues)):
            if i > 0:
                text+=','
            text+=self.toString(i,afterDecimalPoint)
        return text

    def toString(self,attIndex:int,afterDecimalPoint:int)->str:
        text=""
        if self.isMissing(attIndex):
            text+="?"
        else:
            if self.m_Dataset is None:
                text+=Utils.doubleToString(self.value(attIndex),afterDecimalPoint)
            else:
                if self.m_Dataset.attribute(attIndex).type() == Attribute.NUMERIC:
                    text+=Utils.doubleToString(self.value(attIndex),afterDecimalPoint)
                else:
                    text+=Utils.quote(self.stringValue(attIndex))
        return text


    def setDataset(self,inst:'Instances'=None):
        self.m_Dataset=inst

    def setClassMissing(self):
        classIndex=self.classIndex()
        if classIndex < 0:
            raise Exception("Class is not set!")
        self.setMissing(classIndex)

    def setMissing(self,attIndex):
        self.setValue(attIndex,Utils.missingValue())

    def value(self,index:int):
        return self.m_AttValues[index]

    def isMissing(self,attrIndex:int):
        return Utils.isMissingValue(self.m_AttValues[attrIndex])

    def weight(self):
        return self.m_Weight

    def index(self,pos:int):
        return pos

    def isMissingSparse(self,index:int):
        if Utils.isMissingValue(self.valueSparse(index)):
            return True
        return False

    def valueSparse(self,index:int):
        return self.m_AttValues[index]

    def stringValue(self,index:int):
        return self.m_Dataset.attribute(index).value(self.value(index))

    def attribute(self,index:int)->Attribute:
        return self.m_Dataset.attribute(index)

    def setValue(self,index:int,value):
        self.m_AttValues[index]=value

    def deleteAttributeAt(self,pos:int):
        if pos >= 0 and pos < len(self.m_AttValues):
            self.m_AttValues.pop(pos)

    def classIndex(self):
        return self.m_Dataset.classIndex()

    def classIsMissing(self):
        classIndex=self.classIndex()
        return self.isMissing(classIndex)

    def classValue(self):
        classIndex=self.classIndex()
        return self.value(classIndex)

    def copy(self):
        result=Instance(self)
        result.m_Dataset=self.m_Dataset
        return result

    def dataset(self)->'Instances':
        return self.m_Dataset

    def classAttribute(self)->Attribute:
        return self.m_Dataset.classAttribute()

    def numClasses(self):
        return self.m_Dataset.numClasses()

    def numValues(self):
        return len(self.m_AttValues)


    #insertAttributeAt

#TODO 将所有数据处理成float,衍生Instance类
class Instances(object):
    def __init__(self, a0, a1=None,a2=None):
        self.index=0
        if isinstance(a0, dict) and a1 is None and a2 is None:
            self.m_RelationName=a0.get("relation")
            self.m_Attributes=[]    #type:List[Attribute]
            self.m_Instances=[] #type:List[Instance]
            self.m_ClassIndex=-1
            self.m_NamesToAttributeIndices=None     #type:Dict
            for attr in a0.get("attributes"):
                second=attr[1]
                if isinstance(second,str):
                    if second.lower()=="numeric" or second.lower()=="real":
                        attribute=Attribute(attr[0])
                    else:
                        attribute=Attribute(attr[0],True)
                else:
                    attribute=Attribute(attr[0],attr[1])
                self.m_Attributes.append(attribute)

            for item in a0.get("data"):
                self.add(self.createInstance(item))

            self.m_NamesToAttributeIndices=dict()
            for i in range(self.numAttributes()):
                self.attribute(i).setIndex(i)
                self.m_NamesToAttributeIndices.update({self.attribute(i).name():i})
        elif isinstance(a0, Instances) and isinstance(a1,int) and a2 is None:
            self.initialize(a0, a1)
        elif isinstance(a0,Instances) and a1 is None and a2 is None:
            self.__init__(a0,a0.numInstances())
            a0.copyInstances(0, a0.numInstances(), self)
        elif isinstance(a0,Instances) and isinstance(a1,int) and isinstance(a2,int):
            self.__init__(a0,a2)
            a0.copyInstances(a1,a2,self)
        elif isinstance(a0,str) and isinstance(a1,list) and isinstance(a2,int):
            names=set()
            nonUniqueNames=""
            for att in a1:
                if att.name() in names:
                    nonUniqueNames+="'"+att.name()+"'"
                names.add(att.name())
            if len(names) != len(a1):
                raise Exception("Attribute names are not unique!"+ " Causes: " + nonUniqueNames)
            names.clear()
            self.m_RelationName=a0
            self.m_ClassIndex=-1
            self.m_Attributes=a1
            self.m_NamesToAttributeIndices=dict()
            for i in range(self.numAttributes()):
                self.attribute(i).setIndex(i)
                self.m_NamesToAttributeIndices.update({self.attribute(i).name():i})
            self.m_Instances=[]     #type:List[Instance]

    def __iter__(self):
        for instance in self.m_Instances:
            yield instance

    def __getitem__(self, item):
        return self.m_Instances[item]

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

    def classAttribute(self)->Attribute:
        return self.attribute(self.m_ClassIndex)

    def numClasses(self):
        if not self.classAttribute().isNominal():
            return 1
        else:
            return self.classAttribute().numValues()

    def numInstances(self):
        return len(self.m_Instances)

    def numAttributes(self):
        return len(self.m_Attributes)

    def instance(self,index:int)->Instance:
        return self.m_Instances[index]

    def randomize(self,randSeed:int):
        random.seed(randSeed)
        for j in range(self.numInstances()-1,0,-1):
            self.swap(j,random.randint(0,j))

    def swap(self,i:int,j:int):
        inst=self.m_Instances[i]
        self.m_Instances[i]=self.m_Instances[j]
        self.m_Instances[j]=inst
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


    def delete(self,index:int=None):
        if index is None:
            self.m_Instances=[]
        else:
            self.m_Instances.pop(index)

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

    def sort(self,attrIndex=None):
        if isinstance(attrIndex,Attribute):
            attrIndex=attrIndex.index()
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
        atts=copy.deepcopy(self.m_Attributes)
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

    def add(self,inst:Instance,index:int=-1):
        newInstance=copy.deepcopy(inst)
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

    def variance(self,attIndex:int):
        if not self.attribute(attIndex).isNumeric():
            raise Exception( "Can't compute variance because attribute is " + "not numeric!")
        mean=sumWeights=0
        var=float("nan")
        for i in range(self.numInstances()):
            if not self.instance(i).isMissing(attIndex):
                weight=self.instance(i).weight()
                value=self.instance(i).value(attIndex)
                if math.isnan(var):
                    mean=value
                    sumWeights=weight
                    var=0
                    continue
                delta=weight*(value-mean)
                sumWeights+=weight
                mean+=delta/sumWeights
                var+=delta*(value-mean)
        if sumWeights <= 1:
            return float("nan")
        var/=sumWeights-1
        if var < 0:
            return 0
        return var

    def meanOrMode(self,attIndex:int):
        if self.attribute(attIndex).isNumeric():
            result=found=0
            for j in range(self.numInstances()):
                if not self.instance(j).isMissing(attIndex):
                    found+=self.instance(j).weight()
                    result+=self.instance(j).weight()*self.instance(j).value(attIndex)
            if found <= 0:
                return 0
            return result/found
        elif self.attribute(attIndex).isNominal():
            counts=[0]*self.attribute(attIndex).numValues()
            for j in range(self.numInstances()):
                if not self.instance(j).isMissing(attIndex):
                    counts[int(self.instance(j).value(attIndex))]+=self.instance(j).weight()
            return Utils.maxIndex(counts)
        return 0

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

    def equalHeaders(self,dataset:'Instances'):
        return self.equalHeadersMsg(dataset) == None

    def equalHeadersMsg(self,dataset:'Instances'):
        if self.m_ClassIndex != dataset.m_ClassIndex:
            return "Class index differ: " + str(self.m_ClassIndex + 1) + " != "+ str(dataset.m_ClassIndex + 1)
        if len(self.m_Attributes) != len(dataset.m_Attributes):
            return "Different number of attributes: " + str(len(self.m_Attributes)) + " != "+ str(len(dataset.m_Attributes))
        for i in range(len(self.m_Attributes)):
            msg=self.attribute(i).equalsMsg(dataset.attribute(i))
            if msg != None:
                return "Attributes differ at position " + str(i + 1) + ":\n" + msg
        return None

    def stratify(self,numFlods:int):
        if numFlods<=1:
            raise Exception("Number of folds must be greater than 1")
        if self.m_ClassIndex < 0:
            raise Exception("Class index is negative (not set)!")
        if self.classAttribute().isNominal():
            index=1
            while index< self.numInstances():
                instance1=self.instance(index-1)
                for j in range(index,self.numInstances()):
                    instance2=self.instance(j)
                    if instance1.classValue() == instance2.classValue() or (instance1.classIsMissing() and instance2.classIsMissing()):
                        self.swap(index,j)
                        index+=1
                index+=1
            self.stratStep(numFlods)

    def stratStep(self,numFolds:int):
        newVec=[] #type:List[Instance]
        start=0
        while len(newVec) < self.numInstances():
            j=start
            while j<self.numInstances():
                newVec.append(self.instance(j))
                j=j+numFolds
            start+=1
        self.m_Instances=newVec

    def trainCV(self,numFolds:int,numFlod:int,randomSeed:int=None)->'Instances':
        if randomSeed is None:
            if numFolds < 2:
                raise Exception("Number of folds must be at least 2!")
            if numFolds > self.numInstances():
                raise Exception("Can't have more folds than instances!")
            numInstForFold=self.numInstances()//numFolds
            if numFlod <self.numInstances()%numFolds:
                numInstForFold+=1
                offset=numFlod
            else:
                offset=self.numInstances()%numFolds
            train=Instances(self,self.numInstances()-numInstForFold)
            first=numFlod*(self.numInstances()//numFolds)+offset
            self.copyInstances(0,first,train)
            self.copyInstances(first+numInstForFold,self.numInstances()-first-numInstForFold,train)
            return train
        else:
            train=self.trainCV(numFolds,numFlod)
            train.randomize(randomSeed)
            return train

    def deleteWithMissingClass(self,attIndex:int=None):
        if attIndex is None:
            if self.m_ClassIndex < 0:
                raise Exception("Class index is negative (not set)!")
            attIndex=self.m_ClassIndex
        newInstances=[] #type:List[Instance]
        for i in range(self.numInstances()):
            if not self.instance(i).isMissing(attIndex):
                newInstances.append(self.instance(i))
        self.m_Instances=newInstances

    def testCV(self,numFolds:int,numFold:int)->'Instances':
        if numFolds < 2:
            raise Exception("Number of folds must be at least 2!")
        if numFolds > self.numInstances():
            raise Exception("Can't have more folds than instances!")
        numInstForFold=self.numInstances()//numFolds
        if numFold <self.numInstances()%numFolds:
            numInstForFold+=1
            offset=numFold
        else:
            offset=self.numInstances()%numFolds
        test=Instances(self,numInstForFold)
        first=numFold*(self.numInstances()//numFolds)+offset
        self.copyInstances(first,numInstForFold,test)
        return test

    def lastInstance(self)->Instance:
        return self.m_Instances[-1]

    def attributeToDoubleArray(self,index:int):
        result=[]
        for i in range(self.numInstances()):
            result.append(self.instance(i).value(index))
        return result

    def enumerateAttributes(self)->List[Attribute]:
        return self.m_Attributes

Utils.debugOut("Instances id:",id(Instances))