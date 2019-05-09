import copy
from typing import *

from core.Instances import Instances, Instance

from core.Range import Range
from filters.Filter import Filter


class Remove(Filter):
    propertyList = {"attributeIndices":""}
    methodList = {"attributeIndices":"setAttributeIndices"}
    def __init__(self):
        super().__init__()
        self.attributeIndices= Range()
        self.m_SelectedAttributes=[]        #type:List
        self.attributeIndices.setInvert(True)

    def setAttributeIndicesArray(self,attributes:List):
        self.setAttributeIndices(Range.indicesToRangeList(attributes))

    def setAttributeIndices(self,rangeList:str):
        self.attributeIndices.setRanges(rangeList)

    def setInvertSelection(self,invert:bool):
        self.attributeIndices.setInvert(not invert)

    def setInputFormat(self,instanceInfo:Instances):
        super().setInputFormat(instanceInfo)
        self.attributeIndices.setUpper(instanceInfo.numAttributes() - 1)
        attributes=[]
        outputClass=-1
        self.m_SelectedAttributes=self.attributeIndices.getSelection()
        if len(self.m_SelectedAttributes) == instanceInfo.numAttributes():
            self.setOutputFormat(instanceInfo)
            self.initOutputLocators(self.getInputFormat(),self.m_SelectedAttributes)
            return True
        for current in self.m_SelectedAttributes:
            if instanceInfo.classIndex() == current:
                outputClass=len(attributes)
            keep=instanceInfo.attribute(current).copy()
            attributes.append(keep)
        self.initInputLocators(self.getInputFormat(),self.m_SelectedAttributes)
        outputFormat=Instances(instanceInfo.relationName(),attributes,0)
        outputFormat.setClassIndex(outputClass)
        self.setOutputFormat(outputFormat)
        return True

    def input(self,instance:Instance):
        if self.getInputFormat() is None:
            raise Exception("No input instance format defined")
        if self.m_NewBatch:
            self.resetQueue()
            self.m_NewBatch=False
        if self.getOutputFormat().numAttributes() == 0:
            return False
        if len(self.m_SelectedAttributes) == self.getInputFormat().numAttributes():
            inst=copy.deepcopy(instance)
            inst.setDataset(None)
        else:
            vals=[0]*self.getOutputFormat().numAttributes()
            for i in range(len(self.m_SelectedAttributes)):
                current=self.m_SelectedAttributes[i]
                vals[i]=instance.value(current)
            inst=Instance(instance.weight(),vals)
        self.copyValues(inst,False,instance.dataset(),self.outputFormatPeek())
        self.push(inst)
        return True