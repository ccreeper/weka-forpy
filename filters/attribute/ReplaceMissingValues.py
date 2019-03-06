from typing import *
from filters.Filter import Filter
from Instances import Instances,Instance
from Capabilities import Capabilities,CapabilityEnum
from Utils import Utils

class ReplaceMissingValues(Filter):
    def __init__(self):
        super().__init__()

    def setInputFormat(self,instanceInfo:Instances):
        super().setInputFormat(instanceInfo)
        self.setOutputFormat(instanceInfo)
        self.m_ModesAndMeans=None
        return True

    def getCapabilities(self,data:Instances=None):
        result=super().getCapabilities()
        result.disableAll()
        result.enableAllAttributes()
        result.enable(CapabilityEnum.MISSING_VALUES)
        result.enableAllClasses()
        result.enable(CapabilityEnum.MISSING_CLASS_VALUES)
        result.enable(CapabilityEnum.NO_CLASS)
        return result

    def input(self,instance:Instance):
        if self.getInputFormat() is None:
            raise Exception("No input instance format defined")
        if self.m_NewBatch:
            self.resetQueue()
            self.m_NewBatch=False
        if self.m_ModesAndMeans is None:
            self.bufferInput(instance)
            return False
        else:
            self.convertInstance(instance)
            return True

    def convertInstance(self,instance:Instance):
        inst=instance
        hasMissing=instance.hasMissingValue()
        if hasMissing:
            vals=[]
            for j in range(instance.numAttributes()):
                if instance.isMissing(j) and self.getInputFormat().classIndex()!=j \
                    and (self.getInputFormat().attribute(j).isNominal() or self.getInputFormat().attribute(j).isNumeric()):
                    vals.append(self.m_ModesAndMeans[j])
                else:
                    vals.append(instance.value(j))
            inst=Instance(instance.weight(),vals)
        inst.setDataset(instance.dataset())
        self.push(inst,not hasMissing)

    def batchFinished(self):
        if self.getInputFormat() is None:
            raise Exception("No input instance format defined")
        if self.m_ModesAndMeans is None:
            sumOfWeights=self.getInputFormat().sumOfWeight()
            counts=[]
            for i in range(self.getInputFormat().numAttributes()):
                if self.getInputFormat().attribute(i).isNominal():
                    counts.append([0]*self.getInputFormat().attribute(i).numValues())
                    if len(counts[i]) > 0:
                        counts[i][0]=sumOfWeights
            sums=[]
            for i in range(self.getInputFormat().numAttributes()):
                sums.append(sumOfWeights)
            results=[0]*self.getInputFormat().numAttributes()
            for j in range(self.getInputFormat().numInstances()):
                inst=self.getInputFormat().instance(j)
                for i in range(inst.numValues()):
                    if not inst.isMissingSparse(i):
                        value=inst.valueSparse(i)
                        if inst.attributeSparse(i).isNominal():
                            if len(counts[inst.index(i)]) > 0:
                                counts[inst.index(i)][int(value)]+=inst.weight()
                                counts[inst.index(i)][0]-=inst.weight()
                        elif inst.attributeSparse(i).isNumeric():
                            results[inst.index(i)]+=inst.weight()*inst.valueSparse(i)
                    else:
                        if inst.attributeSparse(i).isNominal():
                            if len(counts[inst.index(i)]) > 0 :
                                counts[inst.index(i)][0]-=inst.weight()
                        elif inst.attributeSparse(i).isNumeric():
                            sums[inst.index(i)]-=inst.weight()
            self.m_ModesAndMeans=[]
            for i in range(self.getInputFormat().numAttributes()):
                if self.getInputFormat().attribute(i).isNominal():
                    if len(counts[i]) == 0:
                        self.m_ModesAndMeans.append(Utils.missingValue())
                    else:
                        self.m_ModesAndMeans.append(Utils.maxIndex(counts[i]))
                elif self.getInputFormat().attribute(i).isNumeric():
                    if Utils.gr(sums[i],0):
                        self.m_ModesAndMeans.append(results[i]/sums[i])
            for i in range(self.getInputFormat().numInstances()):
                self.convertInstance(self.getInputFormat().instance(i))
        self.flushInput()
        self.m_NewBatch=True
        return self.numPendingOutput() != 0

