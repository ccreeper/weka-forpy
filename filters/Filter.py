import copy
from queue import Queue
from typing import *

from core.Capabilities import Capabilities, CapabilityEnum
from core.Instances import Instances, Instance
from core.StringLocator import StringLocator

from core.Utils import Utils


class Filter():
    propertyList=[]
    methodList = []
    def __init__(self):
        self.m_OutputFormat=None #type:Instances
        self.m_OutputQueue=None     #type:Queue
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
    def getAllProperties(cls):
        return cls.propertyList

    @classmethod
    def getAllMethods(cls):
        return cls.methodList


    def setInputFormat(self,instanceInfo:Instances):
        self.testInputFormat(instanceInfo)
        self.m_InputFormat=instanceInfo.stringFreeStructure()
        self.m_OutputFormat=None        #type:Instances
        self.m_OutputQueue=Queue()
        self.m_NewBatch=True
        self.m_FirstBatchDone=False
        self.initInputLocators(self.m_InputFormat,None)
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

    def setOutputFormat(self, outputFormat: Instances=None):
        if outputFormat is not None:
            self.m_OutputFormat = outputFormat.stringFreeStructure()
            self.initOutputLocators(self.m_OutputFormat)
            relationName = outputFormat.relationName() + "-" +self.__class__.__name__
            self.m_OutputFormat.setRelationName(relationName)
        else:
            self.m_OutputFormat=None
        self.m_OutputQueue=Queue()

    def push(self,instance:Instance,copyInstance:bool=True):
        if instance is not None:
            if instance.dataset() is not None:
                if copyInstance:
                    instance=copy.deepcopy(instance)
                self.copyValues(instance,False)
            instance.setDataset(self.m_OutputFormat)
            self.m_OutputQueue.put(instance)

    @overload
    def copyValues(self,instance:Instance,isInput:bool):...
    @overload
    def copyValues(self,instance:Instance,instSrcCompat:bool,srcDataset:Instances,destDataset:Instances):...
    def copyValues(self,instance:Instance,a0:bool,a1:Instances=None,a2:Instances=None):
        if a1 is None and a2 is None:
            if a0:
                StringLocator.copyStringValues(instance,self.m_InputFormat,self.m_InputStringAtts)
            else:
                StringLocator.copyStringValues(instance,self.m_OutputFormat,self.m_OutputStringAtts)
        else:
            StringLocator.copyStringValues(instance,a0,a1,self.m_InputStringAtts,a2,self.m_OutputStringAtts)


    def initOutputLocators(self,data:Instances,indices:List=None):
        if indices is None:
            self.m_OutputStringAtts=StringLocator(data)
        else:
            self.m_OutputStringAtts=StringLocator(data,indices)

    def getInputFormat(self):
        return self.m_InputFormat

    def outputFormatPeek(self):
        return self.m_OutputFormat

    def resetQueue(self):
        self.m_OutputQueue=Queue()

    def initInputLocators(self,data:Instances,indices:List=None):
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
            instance=copy.deepcopy(instance)
            self.m_InputFormat.add(instance)


    def getOutputFormat(self):
        print("output format num instances:",self.m_OutputFormat.numInstances())
        return Instances(self.m_OutputFormat,0)


    @classmethod
    def useFilter(cls,data:Instances,filter:'Filter'):
        for i in range(data.numInstances()):
            filter.input(data.instance(i))
        filter.batchFinished()
        newData=filter.getOutputFormat()
        Utils.debugOut("Queue size:", filter.m_OutputQueue.qsize())
        processed=filter.output()
        while processed is not None:
            newData.add(processed)
            processed=filter.output()

        return newData
