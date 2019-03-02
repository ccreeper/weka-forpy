from Instances import Instances,Instance
from core.OptionHandler import OptionHandler
from typing import *
from Capabilities import Capabilities,CapabilityEnum
from StringLocator import StringLocator
from queue import Queue

from core.OptionHandler import OptionHandler


class Filter():
    m_Methods = []
    def __init__(self):
        self.m_OutputFormat=None #type:Instances
        self.m_OutputQueue=Queue()
        self.m_InputFormat=None #type:Instances
        self.m_NewBatch=True
        self.m_FirstBatchDone=False
        self.m_Debug=False
        self.m_DoNotCheckCapabilities=False
        self.m_InputStringAtts=None     #type:StringLocator

    def isNewBatch(self):
        return self.m_NewBatch

    def isFirstBatchDone(self):
        return self.m_FirstBatchDone

    @classmethod
    def getMethods(cls):
        return cls.m_Methods

    def setInputFormat(self,instanceInfo:Instances):
        self.testInputFormat(instanceInfo)
        self.m_InputFormat=instanceInfo.stringFreeStructure()
        self.m_OutputFormat=None        #type:Instances
        self.m_OutputQueue=Queue()
        self.m_NewBatch=True
        self.m_FirstBatchDone=False
        return False

    def testInputFormat(self,instanceInfo:Instances):
        self.getCapabilities(instanceInfo).testWithFail(instanceInfo)

    def getCapabilities(self,data:Instances=None):
        if data is None:
            result=Capabilities(self)
            result.enableAll()
            result.setMinimumNumberInstances(0)
            return result
        result=self.getCapabilities()
        if data.classIndex() == -1:
            classes=result.getClassCapabilities()
            iter=classes.capabilities()
            for item in iter:
                if item != CapabilityEnum.NO_CLASS:
                    result.disable(item)
                    result.disableDependency(item)
        else:
            result.disable(CapabilityEnum.NO_CLASS)
            result.disableDependency(CapabilityEnum.NO_CLASS)
        return result

    def setOutputFormat(self, outputFormat: Instances):
        if outputFormat is not None:
            self.m_OutputFormat = outputFormat.stringFreeStructure()
            self.initOutputLocators(self.m_OutputFormat,None)
            relationName = outputFormat.relationName() + "-" +self.__class__.__name__
            if isinstance(self,OptionHandler):
                options=self.getOptions()
                for option in options:
                    relationName+=option.strip()
            self.m_OutputFormat.setRelationName(relationName)
        else:
            self.m_OutputFormat=None
        self.m_OutputQueue=Queue()

    def initOutputLocators(self,data:Instances,indices:List):
        if indices is None:
            self.m_OutputStringAtts=StringLocator(data)
        else:
            self.m_OutputStringAtts=StringLocator(data,indices)

    def initInputLocators(self,data:Instances,indices:List):
        if indices is None:
            self.m_InputStringAtts=StringLocator(data)
        else:
            self.m_InputStringAtts=StringLocator(data,indices)

    def input(self,instance:Instance):
        if self.m_InputFormat is None:
            raise Exception("No input instance format defined")
        if self.m_NewBatch:
            self.m_OutputQueue=Queue()
            self.m_NewBatch=False
        self.bufferInput(instance)
        return False

    def batchFinished(self):
        if self.m_InputFormat is None:
            raise Exception("No input instance format defined")
        self.flushInput()
        self.m_NewBatch=True
        self.m_FirstBatchDone=True
        if self.m_OutputQueue.empty():
            if len(self.m_OutputStringAtts.getAttributeIndices())>0:
                self.m_OutputFormat=self.m_OutputFormat.stringFreeStructure()
                self.m_OutputStringAtts=StringLocator(self.m_OutputFormat,self.m_OutputStringAtts.getAllowedIndices())
        return self.numPendingOutput() != 0

    def numPendingOutput(self):
        if self.m_OutputFormat is None:
            raise Exception("No output instance format defined")
        return self.m_OutputQueue.qsize()

    def flushInput(self):
        if len(self.m_InputStringAtts.getAttributeIndices())>0:
            self.m_InputFormat=self.m_InputFormat.stringFreeStructure()
            self.m_InputStringAtts=StringLocator(self.m_InputFormat,self.m_InputStringAtts.getAllowedIndices())
        else:
            self.m_InputFormat.delete()

    def output(self)->Instance:
        if not self.m_OutputQueue.empty():
            result=self.m_OutputQueue.get()
            return result
        return None

    def bufferInput(self,instance:Instance):
        if instance is not None:
            instance=instance.copy()
            self.m_InputFormat.add(instance)

    def getOutputFormat(self):
        return Instances(self.m_OutputFormat,0)


    @classmethod
    def useFilter(cls,data:Instances,filter:'Filter'):
        for i in range(data.numInstances()):
            filter.input(data.instance(i))
        newData=filter.getOutputFormat()
        processed=filter.output()
        while processed is not None:
            newData.add(processed)
            processed=filter.output()
        return newData
