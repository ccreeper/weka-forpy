from filters.Filter import Filter
from Range import Range
from OptionHandler import OptionHandler
from Instances import Instances,Instance
from typing import *

class Remove(Filter,OptionHandler):
    def __init__(self):
        super().__init__()
        self.m_SelectCols=Range()
        self.m_SelectedAttributes=[]        #type:List
        self.m_SelectCols.setInvert(True)

    def setAttributeIndicesArray(self,attributes:List):
        self.setAttributeIndices(Range.indicesToRangeList(attributes))

    def setAttributeIndices(self,rangeList:str):
        self.m_SelectCols.setRanges(rangeList)

    def setInvertSelection(self,invert:bool):
        self.m_SelectCols.setInvert(not invert)

    def setInputFormat(self,instanceInfo:Instances):
        super().setInputFormat(instanceInfo)
        self.m_SelectCols.setUpper(instanceInfo.numAttributes()-1)
        attributes=[]
        outputClass=-1
        self.m_SelectedAttributes=self.m_SelectCols.getSelection()
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

    def getInputFormat(self)->Instances:
        return self.m_InputFormat