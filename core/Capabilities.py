from typing import *
from enum import Enum
from CapabilitiesHandler import CapabilitiesHandler
from configparser import ConfigParser
import classifiers.UpdateableClassifier
import clusterers.UpdateableClusterer
from Instances import Instances
from CapabilitiesIgnorer import CapabilitiesIgnorer
from Attributes import Attribute
import importlib
import sys

class CapabilityError(Exception):
    def __init__(self,errorInfo):
        super().__init__(self)
        self.errorInfo=errorInfo
    def __str__(self):
        return self.errorInfo

class Capabilities():
    ATTRIBUTE = 1
    CLASS = 2
    ATTRIBUTE_CAPABILITY = 4
    CLASS_CAPABILITY = 8
    OTHER_CAPABILITY = 16
    INTERFACE_DEFINED_CAPABILITIES = set()  # type:Set[type]
    try:
        cf = ConfigParser()
        cf.read("./config/Capabilities.conf")
        kvs = cf.items("Capabilities")
        for item in kvs:
            model = importlib.import_module(item[1])
            strli = item[1].split('.')
            cls = getattr(model, strli[-1])
            INTERFACE_DEFINED_CAPABILITIES.add(cls)
        print(INTERFACE_DEFINED_CAPABILITIES)
    except BaseException:
        pass

    def __init__(self, owner):
        self.m_Capabilities = set()  # type:Set[Capability]
        self.m_Dependencies = set()  # type:Set[Capability]
        self.m_MinimumNumberInstances = 1
        self.m_FailReason=None      #type:CapabilityError

        self.setOwner(owner)
        if isinstance(owner, classifiers.UpdateableClassifier.UpdateableClassifier) or isinstance(owner,
                                                                                                  clusterers.UpdateableClusterer.UpdateableClusterer):
            self.setMinimumNumberInstances(0)

    def setMinimumNumberInstances(self, value: int):
        if value >= 0:
            self.m_MinimumNumberInstances = value

    def setOwner(self, value:CapabilitiesHandler):
        self.m_Owner = value
        self.m_InterfaceDefinedCapabilities = set()
        if self.m_Owner is not None:
            for c in self.INTERFACE_DEFINED_CAPABILITIES:
                if isinstance(value, c):
                    self.m_InterfaceDefinedCapabilities.add(c)

    def enableAll(self):
        self.enableAllAttributes()
        self.enableAllAttributeDependencies()
        self.enableAllClasses()
        self.enableAllClassDependencies()
        self.enable(CapabilityEnum.MISSING_VALUES)
        self.enable(CapabilityEnum.MISSING_CLASS_VALUES)

    def disableAll(self):
        self.disableAllAttributes()
        self.disableAllAttributeDependencies()
        self.disableAllClasses()
        self.disableAllClassDependencies()
        self.disable(CapabilityEnum.MISSING_VALUES)
        self.disable(CapabilityEnum.MISSING_CLASS_VALUES)
        self.disable(CapabilityEnum.NO_CLASS)


    def disableAllClassDependencies(self):
        for cap in CapabilityEnum:
            if cap.value.isClass():
                self.disableDependency(cap)


    def disableAllClasses(self):
        for cap in CapabilityEnum:
            if cap.value.isClass():
                self.disable(cap)

    def disableAllAttributeDependencies(self):
        for cap in CapabilityEnum:
            if cap.value.isAttribute():
                self.disableDependency(cap)

    def disableAllAttributes(self):
        for cap in CapabilityEnum:
            if cap.value.isAttribute():
                self.disable(cap)

    def disableDependency(self,c:'CapabilityEnum'):
        if c == CapabilityEnum.NOMINAL_ATTRIBUTES:
            self.enableDependency(CapabilityEnum.BINARY_ATTRIBUTES)
        elif c == CapabilityEnum.BINARY_ATTRIBUTES:
            self.enableDependency(CapabilityEnum.UNARY_ATTRIBUTES)
        elif c == CapabilityEnum.UNARY_ATTRIBUTES:
            self.enableDependency(CapabilityEnum.EMPTY_NOMINAL_ATTRIBUTES)
        elif c == CapabilityEnum.NOMINAL_CLASS:
            self.enableDependency(CapabilityEnum.BINARY_CLASS)
        elif c == CapabilityEnum.BINARY_CLASS:
            self.disableDependency(CapabilityEnum.UNARY_CLASS)
        elif c == CapabilityEnum.UNARY_CLASS:
            self.disableDependency(CapabilityEnum.EMPTY_NOMINAL_CLASS)
        self.m_Dependencies.remove(c)

    def disable(self, c: 'CapabilityEnum'):
        if c == CapabilityEnum.NOMINAL_ATTRIBUTES:
            self.disable(CapabilityEnum.BINARY_ATTRIBUTES)
        elif c == CapabilityEnum.BINARY_ATTRIBUTES:
            self.disable(CapabilityEnum.UNARY_ATTRIBUTES)
        elif c == CapabilityEnum.UNARY_ATTRIBUTES:
            self.disable(CapabilityEnum.EMPTY_NOMINAL_ATTRIBUTES)
        elif c == CapabilityEnum.NOMINAL_CLASS:
            self.disable(CapabilityEnum.BINARY_CLASS)
        elif c == CapabilityEnum.BINARY_CLASS:
            self.disable(CapabilityEnum.UNARY_CLASS)
        elif c == CapabilityEnum.UNARY_CLASS:
            self.disable(CapabilityEnum.EMPTY_NOMINAL_CLASS)
        self.m_Capabilities.remove(c)

    def enableAllClassDependencies(self):
        for cap in CapabilityEnum:
            if cap.value.isClass():
                self.enableDependency(cap)

    def enableAllClasses(self):
        for cap in CapabilityEnum:
            if cap.value.isClass():
                self.enable(cap)

    def enableAllAttributeDependencies(self):
        for cap in CapabilityEnum:
            if cap.value.isAttribute():
                self.enableDependency(cap)

    def enableDependency(self, c: 'CapabilityEnum'):
        if c == CapabilityEnum.NOMINAL_ATTRIBUTES:
            self.enableDependency(CapabilityEnum.BINARY_ATTRIBUTES)
        elif c == CapabilityEnum.BINARY_ATTRIBUTES:
            self.enableDependency(CapabilityEnum.UNARY_ATTRIBUTES)
        elif c == CapabilityEnum.UNARY_ATTRIBUTES:
            self.enableDependency(CapabilityEnum.EMPTY_NOMINAL_ATTRIBUTES)
        elif c == CapabilityEnum.NOMINAL_CLASS:
            self.enableDependency(CapabilityEnum.BINARY_CLASS)
        self.m_Dependencies.add(c)

    def enableAllAttributes(self):
        for cap in CapabilityEnum:
            if cap.value.isAttribute():
                self.enable(cap)

    def enable(self, c: 'CapabilityEnum'):
        if c == CapabilityEnum.NOMINAL_ATTRIBUTES:
            self.enable(CapabilityEnum.BINARY_ATTRIBUTES)
        elif c == CapabilityEnum.BINARY_ATTRIBUTES:
            self.enable(CapabilityEnum.UNARY_ATTRIBUTES)
        elif c == CapabilityEnum.UNARY_ATTRIBUTES:
            self.enable(CapabilityEnum.EMPTY_NOMINAL_ATTRIBUTES)
        elif c == CapabilityEnum.NOMINAL_CLASS:
            self.enable(CapabilityEnum.BINARY_CLASS)
        self.m_Capabilities.add(c)

    def getOwner(self)->CapabilitiesHandler:
        return self.m_Owner

    def testWithFail(self,data:Instances):
        if not self.testInstances(data):
            raise self.m_FailReason

    def testAttribute(self,att:Attribute,isClass:bool=False):
        if self.doNotCheckCapabilities():
            return True
        if att.type() == Attribute.NOMINAL:
            if isClass:
                cap=CapabilityEnum.NOMINAL_CLASS
                capBinary=CapabilityEnum.BINARY_CLASS
                capUnary=CapabilityEnum.UNARY_CLASS
                capEmpty=CapabilityEnum.EMPTY_NOMINAL_CLASS
            else:
                cap=CapabilityEnum.NOMINAL_ATTRIBUTES
                capBinary=CapabilityEnum.BINARY_ATTRIBUTES
                capUnary=CapabilityEnum.UNARY_ATTRIBUTES
                capEmpty=CapabilityEnum.EMPTY_NOMINAL_ATTRIBUTES
            if self.handles(cap) and att.numValues() >2:
                return False
            elif self.handles(capBinary) and att.numValues() == 2:
                return False
            elif self.handles(capUnary) and att.numValues() == 1:
                return False
            elif self.handles(capEmpty) and att.numValues() == 0:
                return False
            return False
        elif att.type() == Attribute.NUMERIC:
            if isClass:
                cap=CapabilityEnum.NUMERIC_CLASS
            else:
                cap=CapabilityEnum.NUMERIC_ATTRIBUTES
            if not self.handles(cap):
                return False
        elif att.type() == Attribute.DATE:
            if isClass:
                cap=CapabilityEnum.DATE_CLASS
            else:
                cap=CapabilityEnum.DATE_ATTRIBUTES
            if not self.handles(cap):
                return False
        elif att.type() == Attribute.STRING:
            if isClass:
                cap=CapabilityEnum.STRING_CLASS
            else:
                cap=CapabilityEnum.STRING_ATTRIBUTES
            if not self.handles(cap):
                return False
        else:
            return False


    def testInstances(self,data:Instances,*args):
        if len(args) == 0:
            self.testInstances(data,0,data.numAttributes()-1)
            return
        fromIndex=args[0]
        toIndex=args[1]
        if self.doNotCheckCapabilities():
            return True
        if len(self.m_Capabilities)==0 or (len(self.m_Capabilities)==1 and self.handles(CapabilityEnum.NO_CLASS)):
            sys.stderr.write("No capabilities set!")
        if toIndex - fromIndex <0:
            self.m_FailReason=CapabilityError("No attributes!")
            return False
        testClass = data.classIndex()>-1 and data.classIndex()>=fromIndex and data.classIndex()<=toIndex
        for i in range(fromIndex,toIndex+1):
            att=data.attribute(i)
            if i == data.classIndex():
                continue
            if not self.testAttribute(att):
                return False
        if not self.handles(CapabilityEnum.NO_CLASS) and data.classIndex() == -1:
            self.m_FailReason=CapabilityError("Class attribute not set!")
            return False

        if self.handles(CapabilityEnum.NO_CLASS) and data.classIndex() >-1:
            cap=self.getClassCapabilities()
            cap.disable(CapabilityEnum.NO_CLASS)
            iter=cap.capabilities()
            if len(iter) == 0:
                self.m_FailReason=CapabilityError("Cannot handle any class attribute!")
                return False
        if testClass and not self.handles(CapabilityEnum.NO_CLASS):
            att=data.classAttribute()
            if not self.testAttribute(att,True):
                return False
            if not self.handles(CapabilityEnum.MISSING_CLASS_VALUES):
                for i in range(data.numInstances()):
                    if data.instance(i).classIsMissing():
                        self.m_FailReason=CapabilityError("Cannot handle missing class values!")
                        return False
            else:
                hasClass=0
                for i in range(data.numInstances()):
                    if not data.instance(i).classIsMissing():
                        hasClass+=1
                if hasClass < self.getMinimumNumberInstances():
                    self.m_FailReason=CapabilityError("Not enough training instances with class labels (required: "\
                                                      + str(self.getMinimumNumberInstances())\
                                                      + ", provided: "\
                                                      + str(hasClass)\
                                                      + ")!")
                    return False
        missing=False
        for i in range(data.numInstances()):
            inst=data.instance(i)
            if not self.handles(CapabilityEnum.MISSING_VALUES):
                #TODO 使用稀疏矩阵pass
                # if isinstance(inst)
                #     pass
                #else
                for n in range(fromIndex,toIndex+1):
                    if n == inst.classIndex():
                        continue
                    if inst.isMissing(n):
                        missing=True
                        break
                if missing:
                    self.m_FailReason=CapabilityError("Cannot handle missing values!")
                    return False
        if data.numInstances() < self.getMinimumNumberInstances():
            self.m_FailReason=CapabilityError("Not enough training instances (required: "
                                        + str(self.getMinimumNumberInstances()) + ", provided: "
                                        + str(data.numInstances())+ ")!")
            return False
        # if self.handles(CapabilityEnum.ONLY_MULTIINSTANCE):
        #     if data.numAttributes() != 3:
        #         return False
        #     if not data.attribute(0).isNominal() or data.classIndex() != data.numAttributes()-1:
        #         return False
        #     owner=self.getOwner()
        #     if isinstance(owner,MultiInstanceCapabilitiesHandler):
        #         handler=owner
        #         cap=handler.getMultiInstanceCapabilities()
        #         if data.numInstances()>0 and data.attribute(1).numValues()>0:
        #             result=cap.testAttribute(data.attribute(1))
        return True

    def getMinimumNumberInstances(self):
        return self.m_MinimumNumberInstances

    def capabilities(self):
        return self.m_Capabilities

    def getClassCapabilities(self):
        result=Capabilities(self.getOwner())
        for cap in CapabilityEnum:
            if cap.value.isClassCapability():
                if self.handles(cap):
                    result.m_Capabilities.add(cap)
        return result



    def handles(self,c:'CapabilityEnum')->bool:
        return c in self.m_Capabilities

    def doNotCheckCapabilities(self):
        owner=self.getOwner()
        if owner is not None and isinstance(owner,CapabilitiesIgnorer):
            return owner.getDoNotCheckCapabilities()
        return False



class Capability():
    def __init__(self, flags: int, display: str):
        self.m_Flags = flags
        self.m_Display = display

    def isAttribute(self):
        return (self.m_Flags & Capabilities.ATTRIBUTE) == Capabilities.ATTRIBUTE

    def isClass(self):
        return (self.m_Flags & Capabilities.CLASS) == Capabilities.CLASS

    def isAttributeCapability(self):
        return (self.m_Flags & Capabilities.ATTRIBUTE_CAPABILITY) == Capabilities.ATTRIBUTE_CAPABILITY

    def isOtherCapability(self):
        return (self.m_Flags & Capabilities.OTHER_CAPABILITY) == Capabilities.OTHER_CAPABILITY

    def isClassCapability(self):
        return (self.m_Flags & Capabilities.CLASS_CAPABILITY) == Capabilities.CLASS_CAPABILITY

    def __str__(self):
        return self.m_Display


class CapabilityEnum(Enum):
    NOMINAL_ATTRIBUTES = Capability(Capabilities.ATTRIBUTE + Capabilities.ATTRIBUTE_CAPABILITY, "Nominal attributes"),
    BINARY_ATTRIBUTES = Capability(Capabilities.ATTRIBUTE + Capabilities.ATTRIBUTE_CAPABILITY, "Binary attributes"),
    UNARY_ATTRIBUTES = Capability(Capabilities.ATTRIBUTE + Capabilities.ATTRIBUTE_CAPABILITY, "Unary attributes"),
    EMPTY_NOMINAL_ATTRIBUTES = Capability(Capabilities.ATTRIBUTE + Capabilities.ATTRIBUTE_CAPABILITY,"Empty nominal attributes"),
    NUMERIC_ATTRIBUTES = Capability(Capabilities.ATTRIBUTE + Capabilities.ATTRIBUTE_CAPABILITY, "Numeric attributes"),
    DATE_ATTRIBUTES = Capability(Capabilities.ATTRIBUTE + Capabilities.ATTRIBUTE_CAPABILITY, "Date attributes"),
    STRING_ATTRIBUTES = Capability(Capabilities.ATTRIBUTE + Capabilities.ATTRIBUTE_CAPABILITY, "String attributes"),
    RELATIONAL_ATTRIBUTES = Capability(Capabilities.ATTRIBUTE + Capabilities.ATTRIBUTE_CAPABILITY,"Relational attributes"),
    MISSING_VALUES = Capability(Capabilities.ATTRIBUTE_CAPABILITY, "Missing values"),
    NO_CLASS = Capability(Capabilities.CLASS_CAPABILITY, "No class"),
    NOMINAL_CLASS = Capability(Capabilities.CLASS + Capabilities.CLASS_CAPABILITY, "Nominal class"),
    BINARY_CLASS = Capability(Capabilities.ATTRIBUTE + Capabilities.CLASS_CAPABILITY, "Binary class"),
    UNARY_CLASS = Capability(Capabilities.CLASS + Capabilities.CLASS_CAPABILITY, "Unary class"),
    EMPTY_NOMINAL_CLASS = Capability(Capabilities.ATTRIBUTE + Capabilities.CLASS_CAPABILITY, "Empty nominal class"),
    NUMERIC_CLASS = Capability(Capabilities.CLASS + Capabilities.CLASS_CAPABILITY, "Numeric class"),
    DATE_CLASS = Capability(Capabilities.ATTRIBUTE + Capabilities.CLASS_CAPABILITY, "Date class"),
    STRING_CLASS = Capability(Capabilities.CLASS + Capabilities.CLASS_CAPABILITY, "String class"),
    RELATIONAL_CLASS = Capability(Capabilities.ATTRIBUTE + Capabilities.CLASS_CAPABILITY, "Relational class"),
    MISSING_CLASS_VALUES = Capability(Capabilities.CLASS_CAPABILITY, "Missing class values"),
    ONLY_MULTIINSTANCE = Capability(Capabilities.OTHER_CAPABILITY, "Only multi-Instance data")
