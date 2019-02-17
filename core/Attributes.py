from AttributeInfo import DateAttributeInfo,NominalAttributeInfo
from typing import *

class Attribute():
    NUMERIC=0
    NOMINAL=1
    STRING=2
    DATE=3

    def __init__(self,name:str,other=None,index=None):
        self.m_Name=name
        self.m_Type=Attribute.NUMERIC
        self.m_AttributeInfo=None
        self.m_Index=-1
        self.m_Weight=1.0
        if other is not None:
            if isinstance(other,bool):
                if other:
                    self.m_Type=Attribute.STRING
                    self.m_AttributeInfo= NominalAttributeInfo()
            elif isinstance(other,str):
                self.m_Type = Attribute.DATE
                self.m_AttributeInfo = DateAttributeInfo(other)
            elif isinstance(other,list):
                self.m_AttributeInfo=NominalAttributeInfo(other)
                if other is None:
                    self.m_Type=Attribute.STRING
                else:
                    self.m_Type=Attribute.NOMINAL
        if index is not None:
            self.m_Index=index

    def name(self):
        return self.m_Name

    def type(self):
        return self.m_Type

    def setIndex(self,index:int):
        self.m_Index=index

    def isNominal(self):
        return self.m_Type == self.NOMINAL

    def isNumeric(self):
        return self.m_Type == self.NUMERIC or self.m_Type == self.DATE

    def isString(self):
        return self.m_Type == self.STRING

    def index(self):
        return self.m_Index

    def numValues(self):
        if not self.isNominal() and not self.isString():
            return 0
        else:
            return len(self.m_AttributeInfo.m_Values)

    def value(self,index:int)->str:
        if not self.isNominal() and not self.isString():
            return ""
        else:
            val=self.m_AttributeInfo.m_Values[index]
        return str(val)

    #返回该属性的所有值
    def values(self)->List[str]:
        if not self.isNominal() and not self.isString():
            return None
        else:
            return self.m_AttributeInfo.m_Values


    def indexOfValue(self,value:str)->int:
        if not self.isNominal() and not self.isNumeric():
            return -1
        result=self.m_AttributeInfo.m_Hashtable.get(value)
        if result is None:
            result=-1
        return result

    def index(self):
        return self.m_Index

    def weight(self):
        return self.m_Weight

    def setWeight(self,value:float):
        self.m_Weight=value

    def addStringValue(self,value:str):
        if not self.isString():
            return -1
        else:
            index=self.m_AttributeInfo.m_Hashtable.get(value)
            if index is None:
                index=len(self.m_AttributeInfo.m_Hashtable)
                self.m_AttributeInfo.m_Values.append(value)
                self.m_AttributeInfo.m_Hashtable.update({value:index})
            return index

    @classmethod
    def typeToString(self,type:int):
        if type == Attribute.NUMERIC:
            return "numeric"
        elif type == Attribute.STRING:
            return "string"
        elif type == Attribute.NOMINAL:
            return "nominal"
        elif type ==Attribute.DATE:
            return "date"
        else:
            return "unknow"

    @classmethod
    def typeToStringShort(self,type:int):
        if type == Attribute.NUMERIC:
            return "Num"
        elif type == Attribute.STRING:
            return "Str"
        elif type == Attribute.NOMINAL:
            return "Nom"
        elif type ==Attribute.DATE:
            return "Dat"
        else:
            return "???"

    def copy(self,name:str=None):
        if name is None:
            return self.copy(self.m_Name)
        copy=Attribute(name)
        copy.m_Index=self.m_Index
        copy.m_Type=self.m_Type
        copy.m_AttributeInfo=self.m_AttributeInfo
        copy.m_Weight=self.m_Weight
        return copy

    def equalsMsg(self,other:'Attribute')->str:
        if other is None:
            return "Comparing with null object"
        if other.__class__ != self.__class__:
            return "Object has wrong class"
        if self.m_Name != other.m_Name:
            return "Names differ: " + self.m_Name + " != " + other.m_Name
        if self.isNominal() and other.isNominal():
            if len(self.m_AttributeInfo.m_Values) != len(other.m_AttributeInfo.m_Values):
                return "Different number of labels: " + str(len(self.m_AttributeInfo.m_Values)) + " != "+ str(len(other.m_AttributeInfo.m_Values))
            for i in range(len(self.m_AttributeInfo.m_Values)):
                if self.m_AttributeInfo.m_Values[i] != other.m_AttributeInfo.m_Values[i]:
                    return "Labels differ at position " + str((i + 1)) + ": "+ self.m_AttributeInfo.m_Values[i] + " != " + other.m_AttributeInfo.m_Values[i]
        return None

