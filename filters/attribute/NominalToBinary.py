from typing import *
from filters.Filter import Filter
from Instances import Instances,Instance
from Capabilities import Capabilities,CapabilityEnum
from Attributes import Attribute
from Utils import Utils

class NominalToBinary(Filter):
    def __init__(self):
        super().__init__()
        self.m_Indices=None     #type:List[List[int]]
        self.m_Numeric=True
        self.m_TransformAll=False
        self.m_needToTransform=False
        self.m_SpreadAttributeWeight=False

    def getCapabilities(self,data:Instances=None):
        result=super().getCapabilities()
        result.disableAll()
        result.enableAllAttributes()
        result.enable(CapabilityEnum.MISSING_VALUES)
        result.enable(CapabilityEnum.NUMERIC_CLASS)
        result.enable(CapabilityEnum.DATE_CLASS)
        result.enable(CapabilityEnum.NOMINAL_CLASS)
        result.enable(CapabilityEnum.MISSING_CLASS_VALUES)
        return result

    def setInputFormat(self,instanceInfo:Instances):
        super().setInputFormat(instanceInfo)
        if instanceInfo.classIndex() < 0:
            raise Exception("No class has been assigned to the instances")
        self.setOutputFormatBinary()
        self.m_Indices=None
        if instanceInfo.classAttribute().isNominal():
            return True
        return False

    def input(self,instance:Instance):
        if self.getInputFormat() is None:
            raise Exception("No input instance format defined")
        if self.m_NewBatch:
            self.resetQueue()
            self.m_NewBatch=False
        if self.m_Indices is not None or self.getInputFormat().classAttribute().isNominal():
            self.convertInstance(instance.copy())
            return True
        self.bufferInput(instance)
        return False

    def batchFinished(self):
        if self.getInputFormat() is None:
            raise Exception("No input instance format defined")
        if self.m_Indices is None and self.getInputFormat().classAttribute().isNumeric():
            self.computeAverageClassValues()
            self.setOutputFormatBinary()
            for i in range(self.getInputFormat().numInstances()):
                self.convertInstance(self.getInputFormat().instance(i))
        self.flushInput()
        self.m_NewBatch=True
        return self.numPendingOutput()!=0

    def computeAverageClassValues(self):
        avgClassValues=[[] for i in range(self.getInputFormat().numAttributes())]
        self.m_Indices=[[] for i in range(self.getInputFormat().numAttributes())]
        for j in range(self.getInputFormat().numAttributes()):
            att=self.getInputFormat().attribute(j)
            if att.isNominal():
                avgClassValues[j]=[0]*att.numValues()
                counts=[0]*att.numValues()
                for i in range(self.getInputFormat().numInstances()):
                    instance=self.getInputFormat().instance(i)
                    if not instance.classIsMissing() and not instance.isMissing(j):
                        counts[int(instance.value(j))]+=instance.weight()
                        avgClassValues[j][int(instance.value(j))]+=instance.weight()*instance.weight()
                sums=sum(avgClassValues[j])
                totalCounts=sum(counts)
                if Utils.gr(totalCounts,0):
                    for k in range(att.numValues()):
                        if Utils.gr(counts[k],0):
                            avgClassValues[j][k]/=counts[k]
                        else:
                            avgClassValues[j][k]=sums/totalCounts
                self.m_Indices[j]=Utils.sortDouble(avgClassValues[j])

    def convertInstance(self,inst:Instance):
        if self.getInputFormat().classAttribute().isNominal():
            self.convertInstanceNominal(inst)
        else:
            self.convertInstanceNumeric(inst)

    def convertInstanceNominal(self,instance:Instance):
        if not self.m_needToTransform:
            self.push(instance,False)
            return
        vals=[0]*self.outputFormatPeek().numAttributes()
        attSoFar=0
        for j in range(self.getInputFormat().numAttributes()):
            att=self.getInputFormat().attribute(j)
            if not att.isNominal() or j == self.getInputFormat().classIndex():
                vals[attSoFar]=instance.value(j)
                attSoFar+=1
            else:
                if att.numValues() <= 2 and not self.m_TransformAll:
                    vals[attSoFar]=instance.value(j)
                    attSoFar+=1
                else:
                    if instance.isMissing(j):
                        for k in range(att.numValues()):
                            vals[attSoFar+k]=instance.value(j)
                    else:
                        for k in range(att.numValues()):
                            if k == int(instance.value(j)):
                                vals[attSoFar+k]=1
                            else:
                                vals[attSoFar+k]=0
                    attSoFar+=att.numValues()
        inst=Instance(instance.weight(),vals)
        self.copyValues(inst,False,instance.dataset(),self.outputFormatPeek())
        self.push(inst)

    def convertInstanceNumeric(self,instance:Instance):
        if not self.m_needToTransform:
            self.push(instance,False)
            return
        vals=[0]*self.outputFormatPeek().numAttributes()
        attSoFar=0
        for j in range(self.getInputFormat().numAttributes()):
            att=self.getInputFormat().attribute(j)
            if not att.isNominal() or j == self.getInputFormat().classIndex():
                vals[attSoFar]=instance.value(j)
                attSoFar+=1
            else:
                if instance.isMissing(j):
                    for k in range(att.numValues()-1):
                        vals[attSoFar+k]=instance.value(j)
                else:
                    k=0
                    while int(instance.value(j)) != self.m_Indices[j][k]:
                        vals[attSoFar+k]=1
                        k+=1
                    while k < att.numValues()-1:
                        vals[attSoFar+k]=0
                        k+=1
                attSoFar+=att.numValues()-1

        inst=Instance(instance.weight(),vals)
        self.copyValues(inst,False,instance.dataset(),self.outputFormatPeek())
        self.push(inst)

    def setOutputFormatBinary(self, outputFormat: Instances=None):
        if self.getInputFormat().classAttribute().isNominal():
            self.setOutputFormatNominal()
        else:
            self.setOutputFormatNumeric()

    def setOutputFormatNominal(self):
        self.m_needToTransform=False
        for i in range(self.getInputFormat().numAttributes()):
            att=self.getInputFormat().attribute(i)
            if att.isNominal() and i != self.getInputFormat().classIndex() and\
                    (att.numValues() > 2 or self.m_TransformAll or self.m_Numeric):
                self.m_needToTransform=True
                break
        if not self.m_needToTransform:
            self.setOutputFormat(self.getInputFormat())
            return
        newClassIndex=self.getInputFormat().classIndex()
        newAtts=[]
        for j in range(self.getInputFormat().numAttributes()):
            att=self.getInputFormat().attribute(j)
            if not att.isNominal() or j == self.getInputFormat().classIndex():
                newAtts.append(att.copy())
            else:
                if att.numValues() <=2 and not self.m_TransformAll:
                    if self.m_Numeric:
                        value=""
                        if att.numValues() == 2:
                            value="="+att.value(1)
                        a=Attribute(att.name()+value)
                        a.setWeight(att.weight())
                        newAtts.append(a)
                    else:
                        newAtts.append(att.copy())
                else:
                    if j < self.getInputFormat().classIndex():
                        newClassIndex+=att.numValues()-1
                    for k in range(att.numValues()):
                        attributeName=att.name()+"="
                        attributeName+=att.value(k)
                        if self.m_Numeric:
                            a=Attribute(attributeName)
                            if self.getSpreadAttributeWeight():
                                a.setWeight(att.weight()/att.numValues())
                            else:
                                a.setWeight(att.weight())
                            newAtts.append(a)
        outputFormat=Instances(self.getInputFormat().relationName(),newAtts,0)
        outputFormat.setClassIndex(newClassIndex)
        self.setOutputFormat(outputFormat)

    def setOutputFormatNumeric(self):
        if self.m_Indices is None:
            self.setOutputFormat()
            return
        self.m_needToTransform=False
        for i in range(self.getInputFormat().numAttributes()):
            att=self.getInputFormat().attribute(i)
            if att.isNominal() and (att.numValues() > 2 or self.m_Numeric or self.m_TransformAll):
                self.m_needToTransform=True
                break
        if not self.m_needToTransform:
            self.setOutputFormat(self.getInputFormat())
            return
        newClassIndex = self.getInputFormat().classIndex()
        newAtts = []
        for j in range(self.getInputFormat().numAttributes()):
            att = self.getInputFormat().attribute(j)
            if not att.isNominal() or j == self.getInputFormat().classIndex():
                newAtts.append(att.copy())
            else:
                if j < self.getInputFormat().classIndex():
                    newClassIndex+=att.numValues()-2
                for k in range(att.numValues()):
                    attributeName=att.name()+"="
                    for l in range(att.numValues()):
                        if l > k:
                            attributeName+=','
                        attributeName+=att.value(att.value(self.m_Indices[j][l]))
                    if self.m_Numeric:
                        a=Attribute(attributeName)
                        if self.getSpreadAttributeWeight():
                            a.setWeight(att.weight()/(att.numValues()-1))
                        else:
                            a.setWeight(att.weight())
                        newAtts.append(a)
                    else:
                        vals=[]
                        vals.append("f")
                        vals.append("t")
                        a=Attribute(attributeName,vals)
                        if self.getSpreadAttributeWeight():
                            a.setWeight(att.weight()/(att.numValues()-1))
                        else:
                            a.setWeight(att.weight())
                        newAtts.append(a)

        outputFormat = Instances(self.getInputFormat().relationName(), newAtts, 0)
        outputFormat.setClassIndex(newClassIndex)
        self.setOutputFormat(outputFormat)


    def getSpreadAttributeWeight(self):
        return self.m_SpreadAttributeWeight
