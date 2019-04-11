from AttributeInfo import DateAttributeInfo,NominalAttributeInfo
from typing import *
from Utils import Utils

class Attribute():
    NUMERIC=0
    NOMINAL=1
    STRING=2
    DATE=3

    def __init__(self, name:str, a0=None, a1=None):
        self.m_Type=Attribute.NUMERIC
        self.m_AttributeInfo=None
        self.m_Index=-1
        self.m_Weight=1.0
        if a0 is None and a1 is None:
            self.m_Name=name
        elif isinstance(a0,bool) and a1 is None:
            self.m_Name=name
            if a0:
                self.m_AttributeInfo=NominalAttributeInfo()
                self.m_Type=Attribute.STRING
        elif isinstance(a0,str) and a1 is None:
            self.m_Name=name
            self.m_Type=Attribute.DATE
            self.m_AttributeInfo=DateAttributeInfo(a0)
        elif isinstance(a0,list) and a1 is None:
            self.m_Name=name
            self.m_Type=Attribute.NOMINAL
            self.m_AttributeInfo=NominalAttributeInfo(a0)
        elif isinstance(a0,int) and a1 is None:
            self.__init__(name)
            self.m_Index=a0
        elif isinstance(a0,str) and isinstance(a1,int):
            self.__init__(name,a0)
            self.m_Index=a1
        elif (isinstance(a0,list) or a0 is None) and isinstance(a1,int):
            self.__init__(name,a0)
            self.m_Index=a1

    def __str__(self):
        text=""
        text+="@attribute "+Utils.quote(self.m_Name)+" "
        if self.m_Type == Attribute.NOMINAL:
            text+="{"
            first=True
            for item in self.m_AttributeInfo.m_Values:
                if first:
                    text+=Utils.quote(item)
                    first=False
                else:
                    text+=","+Utils.quote(item)
            text+="}"
            if self.weight() != 1:
                text+="{"+str(self.weight())+"}"
        elif self.m_Type == Attribute.NUMERIC:
            text+="numeric"
            if self.weight() != 1:
                text+="{"+str(self.weight())+"}"
        elif self.m_Type == Attribute.STRING:
            text+="string"
            if self.weight() != 1:
                text+="{"+str(self.weight())+"}"
        return text


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

    def weight(self):
        return self.m_Weight

    def setWeight(self,value:float):
        self.m_Weight=value

    def addStringValue(self,value,arg0=None):
        if not self.isString():
            return -1
        if isinstance(value,str) and arg0 is None:
            index=self.m_AttributeInfo.m_Hashtable.get(value)
            if index is not None:
                return index
            intIndex=len(self.m_AttributeInfo.m_Hashtable)
            self.m_AttributeInfo.m_Values.append(value)
            self.m_AttributeInfo.m_Hashtable.update({value:intIndex})
            return intIndex
        elif isinstance(value,Attribute) and isinstance(arg0,int):
            store=value.m_AttributeInfo.m_Values[arg0]
            oldIndex=self.m_AttributeInfo.m_Hashtable.get(store)
            if oldIndex is not None:
                return oldIndex
            intIndex=len(self.m_AttributeInfo.m_Values)
            self.m_AttributeInfo.m_Values.append(store)
            self.m_AttributeInfo.m_Hashtable.update({store:intIndex})
            return intIndex

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
    def typeToStringShort(self, attr)->str:
        if isinstance(attr, Attribute):
            return self.typeToStringShort(attr.type())
        elif isinstance(attr,int):
            if attr == Attribute.NUMERIC:
                return "Num"
            elif attr == Attribute.STRING:
                return "Str"
            elif attr == Attribute.NOMINAL:
                return "Nom"
            elif attr ==Attribute.DATE:
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

