from typing import *
from enum import Enum
from CapabilitiesHandler import CapabilitiesHandler
from configparser import ConfigParser
import classifiers.UpdateableClassifier
import clusterers.UpdateableClusterer
import importlib



class Capabilities():
    ATTRIBUTE=1
    CLASS=2
    ATTRIBUTE_CAPABILITY=4
    CLASS_CAPABILITY=8
    OTHER_CAPABILITY=16
    INTERFACE_DEFINED_CAPABILITIES=set()    #type:Set[type]
    #TODO 循环引用问题
    try:
        cf = ConfigParser()
        cf.read("./config/Capabilities.conf")
        kvs = cf.items("Capabilities")
        for item in kvs:
            model=importlib.import_module(item[1])
            strli=item[1].split('.')
            cls=getattr(model,strli[-1])
            INTERFACE_DEFINED_CAPABILITIES.add(cls)
        print(INTERFACE_DEFINED_CAPABILITIES)
    except BaseException:
        pass

    def __init__(self,owner):
        self.m_Capabilities=set() #type:Set[Capability]
        self.m_Dependencies=set() #type:Set[Capability]
        self.m_MinimumNumberInstances=1

        self.setOwner(owner)
        if isinstance(owner,classifiers.UpdateableClassifier.UpdateableClassifier) or isinstance(owner,clusterers.UpdateableClusterer.UpdateableClusterer):
            self.setMinimumNumberInstances(0)

    def setMinimumNumberInstances(self,value:int):
        if value>=0:
            self.m_MinimumNumberInstances=value


    def setOwner(self,value):
        self.m_Owner=value
        self.m_InterfaceDefinedCapabilities=set()
        if self.m_Owner is not None:
            for c in self.INTERFACE_DEFINED_CAPABILITIES:
                if isinstance(value,c):
                    self.m_InterfaceDefinedCapabilities.add(c)

    def enableAll(self):

    def enableAllAttributes(self):
        for cap in CapabilityEnum.value:
            if cap.isAttribute():
                self.

    def enable(self,c:Capability):
        if c == self.CapabilityEnum.get("NOMINAL_ATTRIBUTES"):
            self.enable(self.CapabilityEnum.get("BINARY_ATTRIBUTES"))
        elif c == self.CapabilityEnum.get("BINARY_ATTRIBUTES"):
            self.enable(self.CapabilityEnum.get("UNARY_ATTRIBUTES"))
        elif c == self.CapabilityEnum.get("UNARY_ATTRIBUTES"):
            self.enable(self.CapabilityEnum.get("EMPTY_NOMINAL_ATTRIBUTES"))
        elif c == self.CapabilityEnum.get("NOMINAL_CLASS"):
            self.enable(self.CapabilityEnum.get("BINARY_CLASS"))
        self.m_Capabilities.add(c)

class Capability():
    def __init__(self,flags:int,display:str):
        self.m_Flags=flags
        self.m_Display=display
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
    NOMINAL_ATTRIBUTES=Capability(Capabilities.ATTRIBUTE+Capabilities.ATTRIBUTE_CAPABILITY,"Nominal attributes"),
    BINARY_ATTRIBUTES=Capability(Capabilities.ATTRIBUTE+Capabilities.ATTRIBUTE_CAPABILITY,"Binary attributes"),
    UNARY_ATTRIBUTES=Capability(Capabilities.ATTRIBUTE+Capabilities.ATTRIBUTE_CAPABILITY,"Unary attributes"),
    EMPTY_NOMINAL_ATTRIBUTES=Capability(Capabilities.ATTRIBUTE+Capabilities.ATTRIBUTE_CAPABILITY,"Empty nominal attributes"),
    NUMERIC_ATTRIBUTES=Capability(Capabilities.ATTRIBUTE+Capabilities.ATTRIBUTE_CAPABILITY,"Numeric attributes"),
    DATE_ATTRIBUTES=Capability(Capabilities.ATTRIBUTE+Capabilities.ATTRIBUTE_CAPABILITY,"Date attributes"),
    STRING_ATTRIBUTES=Capability(Capabilities.ATTRIBUTE+Capabilities.ATTRIBUTE_CAPABILITY,"String attributes"),
    RELATIONAL_ATTRIBUTES=Capability(Capabilities.ATTRIBUTE+Capabilities.ATTRIBUTE_CAPABILITY,"Relational attributes"),
    MISSING_VALUES=Capability(Capabilities.ATTRIBUTE_CAPABILITY, "Missing values"),
    NO_CLASS=Capability(Capabilities.CLASS_CAPABILITY,"No class"),
    NOMINAL_CLASS=Capability(Capabilities.CLASS+Capabilities.CLASS_CAPABILITY,"Nominal class"),
    BINARY_CLASS=Capability(Capabilities.ATTRIBUTE+Capabilities.CLASS_CAPABILITY,"Binary class"),
    UNARY_CLASS=Capability(Capabilities.CLASS+Capabilities.CLASS_CAPABILITY,"Unary class"),
    EMPTY_NOMINAL_CLASS=Capability(Capabilities.ATTRIBUTE+Capabilities.CLASS_CAPABILITY,"Empty nominal class"),
    NUMERIC_CLASS=Capability(Capabilities.CLASS+Capabilities.CLASS_CAPABILITY,"Numeric class"),
    DATE_CLASS=Capability(Capabilities.ATTRIBUTE+Capabilities.CLASS_CAPABILITY,"Date class"),
    STRING_CLASS=Capability(Capabilities.CLASS+Capabilities.CLASS_CAPABILITY,"String class"),
    RELATIONAL_CLASS=Capability(Capabilities.ATTRIBUTE+Capabilities.CLASS_CAPABILITY,"Relational class"),
    MISSING_CLASS_VALUES=Capability(Capabilities.CLASS_CAPABILITY,"Missing class values"),
    ONLY_MULTIINSTANCE=Capability(Capabilities.OTHER_CAPABILITY,"Only multi-Instance data")