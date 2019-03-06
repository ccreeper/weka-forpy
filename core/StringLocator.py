from AttributeLocator import AttributeLocator
from typing import *
from Instances import Instances,Instance
from Attributes import Attribute

class StringLocator(AttributeLocator):
    def __init__(self,data:Instances,a0=None,a1=None):
        if a0 is None and a1 is None:
            super().__init__(data,Attribute.STRING)
        elif isinstance(a0,int) and isinstance(a1,int):
            super().__init__(data,Attribute.STRING,a0,a1)
        elif isinstance(a0,List) and a1 is None:
            super().__init__(data,Attribute.STRING,a0)

    def getAttributeIndices(self):
        return self.m_Indices

    def getAllowedIndices(self):
        return self.m_AllowedIndices

    @classmethod
    def copyStringValues(cls,inst:Instance,destDataset:Instances,strAtts:AttributeLocator):
        if inst.dataset() is None:
            raise Exception("Instance has no dataset assigned!!")
        elif inst.dataset().numAttributes() != destDataset.numAttributes():
            raise Exception("Src and Dest differ in # of attributes: "
                      + str(inst.dataset().numAttributes()) + " != "
                      + str(destDataset.numAttributes()))
        cls.copyStringValuesFromSrc(inst,True,inst.dataset(),strAtts,destDataset,strAtts)

    @classmethod
    def copyStringValuesFromSrc(cls,instance:Instance,instSrcCompat:bool,srcDataset:Instances,srcLoc:AttributeLocator,
                         destDataset:Instances,destLoc:AttributeLocator):
        if srcDataset == destDataset:
            return
        if len(srcLoc.getAttributeIndices()) != len(destLoc.getAttributeIndices()):
            raise Exception("Src and Dest string indices differ in length: "
                      + str(len(srcLoc.getAttributeIndices()))+ " != "
                      + str(len(destLoc.getAttributeIndices().length)))
        if len(srcLoc.getLocatorIndices()) != len(destLoc.getLocatorIndices()):
            raise Exception("Src and Dest locator indices differ in length: "
                      + str(len(srcLoc.getLocatorIndices())) + " != "
                      + str(len(destLoc.getLocatorIndices().length)))
        for i in range(len(srcLoc.getAttributeIndices())):
            if instSrcCompat:
                instIndex=srcLoc.getActualIndex(srcLoc.getAttributeIndices()[i])
            else:
                instIndex=destLoc.getActualIndex(destLoc.getAttributeIndices()[i])
            src=srcDataset.attribute(srcLoc.getActualIndex(srcLoc.getAttributeIndices()[i]))
            dest=destDataset.attribute(destLoc.getActualIndex(destLoc.getAttributeIndices()[i]))
            if not instance.isMissing(instIndex):
                valIndex=dest.addStringValue(src,int(instance.value(instIndex)))
                instance.setValue(instIndex,valIndex)
        # srcIndices=srcLoc.getLocatorIndices()
        # destIndices=destLoc.getLocatorIndices()
        # for i in range(len(srcIndices)):
        #     if instSrcCompat:
        #         index=srcLoc.getActualIndex(srcIndices[i])
        #     else:
        #         index=destLoc.getActualIndex(destIndices[i])
        #     if instance.isMissing(index):
        #         continue
        #     valueIndex=int(instance.value(index))
        #     srcStrAttsNew=srcLoc.getLocator(srcIndices[i])
        #     srcDatasetNew=srcStrAttsNew.getData()
        #     destStrAttsNew=destLoc.getLocator(destIndices[i])
        #     destDatasetNew=destStrAttsNew.getData()
