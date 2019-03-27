from typing import *

from Attributes import Attribute
from Instances import Instances,Instance
from SingleIndex import SingleIndex
from Capabilities import Capabilities,CapabilityEnum
from Tag import Tag
from Utils import Utils
from Range import Range
from core.SelectedTag import SelectedTag
from filters.Filter import Filter
import copy


class Add(Filter):
    TAGS_TYPE=[Tag(Attribute.NUMERIC, "NUM", "Numeric attribute"),
               Tag(Attribute.NOMINAL,"NOM","Nominal attribute"),
               Tag(Attribute.STRING,"STR","String attribute"),
               Tag(Attribute.DATE,"DAT","Date attribute")]
    propertyList = {"attributeType":"TAGS_TYPE","attributeName":"unnamed","attributeIndex":"last","nominalLabels":""}
    methodList = {"attributeType":"setAttributeType","attributeName":"setAttributeName",
                  "nominalLabels":"setNominalLabels","attributeIndex":"setAttributeIndex"}
    def __init__(self):
        super().__init__()
        self.attributeType=Attribute.NUMERIC
        self.attributeName= "unnamed"
        self.attributeIndex=SingleIndex("last")
        self.nominalLabels=[]
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
        return SelectedTag(self.attributeType, self.TAGS_TYPE)

    def getWeight(self):
        return self.m_Weight

    def getAttributeName(self):
        return self.attributeName

    def getAttributeIndex(self):
        return self.attributeIndex.getSingleIndex()

    def getDateFormat(self):
        return self.m_DateFormat

    def getNominalLabels(self):
        labelList=""
        for i in range(len(self.nominalLabels)):
            if i==0:
                labelList=self.nominalLabels[i]
            else:
                labelList+=","+self.nominalLabels[i]
        return labelList

    def setAttributeType(self,value:int):
        self.attributeType=self.TAGS_TYPE[value].getID()

    def setAttributeIndex(self,attrIndex:str):
        self.attributeIndex.setSingleIndex(attrIndex)
        self.propertyList.update({"attributeIndex":attrIndex})

    def setAttributeName(self,name:str):
        if name.strip()=="":
            self.attributeName= "unnamed"
        else:
            self.attributeName=name
            self.propertyList.update({"attributeName":name})

    def setNominalLabels(self,labelList:str):
        labels=labelList.split(',')
        self.nominalLabels=labels
        self.propertyList.update({"nominalLabels":labelList})
        # if len(labels)==0:
        #     self.attributeType=Attribute.NUMERIC
        # else:
        #     self.attributeType=Attribute.NOMINAL

    def setWeight(self,weight):
        self.m_Weight=weight

    def getInputFormat(self)->Instances:
        return self.m_InputFormat

    def setInputFormat(self,instanceInfo:Instances):
        super().setInputFormat(instanceInfo)
        self.attributeIndex.setUpper(instanceInfo.numAttributes())
        outputFormat=Instances(instanceInfo,0)
        newAttribute=None
        if self.attributeType == Attribute.NUMERIC:
            newAttribute=Attribute(self.attributeName)
        elif self.attributeType == Attribute.NOMINAL:
            newAttribute=Attribute(self.attributeName, self.nominalLabels)
        elif self.attributeType == Attribute.STRING:
            newAttribute=Attribute(self.attributeName, True)
        elif self.attributeType == Attribute.DATE:
            newAttribute=Attribute(self.attributeName, self.m_DateFormat)
        newAttribute.setWeight(self.getWeight())
        outputFormat.insertAttributeAt(newAttribute, self.attributeIndex.getIndex())
        self.setOutputFormat(outputFormat)
        atts=Range(self.attributeIndex.getSingleIndex())
        atts.setInvert(True)
        atts.setUpper(outputFormat.numAttributes()-1)
        self.initOutputLocators(outputFormat,atts.getSelection())
        return True

    def input(self,instance:Instance):
        if self.getInputFormat() is None:
            raise Exception("No input instance format defined")
        if self.m_NewBatch:
            self.resetQueue()
            self.m_NewBatch=False
        inst=copy.deepcopy(instance)
        self.copyValues(inst,True,inst.dataset(),self.outputFormatPeek())
        inst.setDataset()
        inst.insertAttributeAt(self.attributeIndex.getIndex())
        self.push(inst)
        return True


    # def getCapabilities(self):


