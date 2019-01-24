from typing import *

class SingleIndex():
    def __init__(self,index:str):
        self.m_IndexString=""
        self.m_SelectedIndex=-1
        self.m_Upper=-1
        self.setSingleIndex(index)

    def setUpper(self,newUpper:int):
        if newUpper>=0:
            self.m_Upper=newUpper
            self.setValue()

    def getSingleIndex(self):
        return self.m_IndexString

    def setSingleIndex(self,index:str):
        self.m_IndexString=index
        self.m_SelectedIndex=-1

    def toString(self):
        if self.m_IndexString == "":
            return "No index set"
        return self.m_IndexString

    def getIndex(self):
        return self.m_SelectedIndex

    @classmethod
    def indexToString(cls,index:int):
        return str(index+1)

    def setValue(self):
        if self.m_IndexString.lower() == "first":
            self.m_SelectedIndex=0
        elif self.m_IndexString.lower() == "last":
            self.m_SelectedIndex=self.m_Upper
        else:
            self.m_SelectedIndex=int(self.m_IndexString)-1
            if self.m_SelectedIndex<0 or self.m_SelectedIndex>self.m_Upper:
                self.m_IndexString=""


