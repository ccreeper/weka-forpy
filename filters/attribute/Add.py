from typing import *

from Attributes import Attribute
from Instances import Instances,Instance
from SingleIndex import SingleIndex
from Capabilities import Capabilities,CapabilityEnum
from Tag import Tag
from Utils import Utils

from core.SelectedTag import SelectedTag
from filters.Filter import Filter


class Add(Filter):
    TAGS_TYPE=[Tag(Attribute.NUMERIC,"NUM","Numeric attribute"),
               Tag(Attribute.NOMINAL,"NOM","Nominal attribute"),
               Tag(Attribute.STRING,"STR","String attribute"),
               Tag(Attribute.DATE,"DAT","Date attribute")]

    def __init__(self):
        super().__init__()
        self.m_AttributeType=Attribute.NUMERIC
        self.m_Name="unnamed"
        self.m_Insert=SingleIndex("last")
        self.m_Labels=[]
        self.m_DateFormat="%Y-%m-%d'T'%H:%M:%S"
        self.m_Weight=1

    def getCapabilities(self,data:Instances=None):
        result=super().getCapabilities()
        result.disableAll()
        result.enableAllAttributes()
        result.enable(CapabilityEnum.MISSING_VALUES)
        result.enableAllClasses()
        result.enable(CapabilityEnum.MISSING_CLASS_VALUES)
        result.enable(CapabilityEnum.NO_CLASS)
        return result

    def getAttributeType(self):
        return SelectedTag(self.m_AttributeType,self.TAGS_TYPE)

    def getWeight(self):
        return self.m_Weight

    def getAttributeName(self):
        return self.m_Name

    def getAttributeIndex(self):
        return self.m_Insert.getSingleIndex()

    def getDateFormat(self):
        return self.m_DateFormat

    def getNominalLabels(self):
        labelList=""
        for i in range(len(self.m_Labels)):
            if i==0:
                labelList=self.m_Labels[i]
            else:
                labelList+=","+self.m_Labels[i]
        return labelList

    def setAttributeType(self,value:SelectedTag):
        if value.getTags() == self.TAGS_TYPE:
            self.m_AttributeType=value.getSelectedTag().getID()

    def setAttributeIndex(self,attrIndex:str):
        self.m_Insert.setSingleIndex(attrIndex)

    def setAttributeName(self,name:str):
        if name.strip()=="":
            self.m_Name="unnamed"
        else:
            self.m_Name=name

    def setNominalLabels(self,labelList:str):
        labels=[]
        commaLoc=labelList.index(',')
        while commaLoc >= 0:
            label=labelList[0:commaLoc].strip()
            if label != "":
                labels.append(label)
            labelList=labelList[commaLoc+1:]
        label=labelList.strip()
        if label != "":
            labels.append(label)

        self.m_Labels=labels
        if len(labels)==0:
            self.m_AttributeType=Attribute.NUMERIC
        else:
            self.m_AttributeType=Attribute.NOMINAL

    def setWeight(self,weight):
        self.m_Weight=weight

    def getInputFormat(self)->Instances:
        return self.m_InputFormat

    def setInputFormat(self,instanceInfo:Instances):
        super().setInputFormat(instanceInfo)
        self.m_Insert.setUpper(instanceInfo.numAttributes())
        outputFormat=Instances(instanceInfo,0)
        newAttribute=None
        if self.m_AttributeType == Attribute.NUMERIC:
            newAttribute=Attribute(self.m_Name)
        elif self.m_AttributeType == Attribute.NOMINAL:
            newAttribute=Attribute(self.m_Name,self.m_Labels)
        elif self.m_AttributeType == Attribute.STRING:
            newAttribute=Attribute(self.m_Name,True)
        elif self.m_AttributeType == Attribute.DATE:
            newAttribute=Attribute(self.m_Name,self.m_DateFormat)
        newAttribute.setWeight(self.getWeight())
        outputFormat.insertAttributeAt(newAttribute,self.m_Insert.getIndex())
        self.setOutputFormat(outputFormat)
        return True

    def input(self,instance:Instance):
        if self.getInputFormat() is None:
            raise Exception("No input instance format defined")
        if self.m_NewBatch:
            self.resetQueue()
            self.m_NewBatch=False
        inst=instance.copy()
        self.copyValues(inst,True,inst.dataset(),self.outputFormatPeek())
        inst.setDataset()
        inst.insertAttributeAt(self.m_Insert.getIndex())
        self.push(inst)
        return True



    # def getCapabilities(self):


