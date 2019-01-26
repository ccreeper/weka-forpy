from typing import *

class Tag():
    def __init__(self,ident:int,identStr:str,readable:str,upperCase:bool=True):
        self.m_ID=ident
        if len(identStr)==0:
            self.m_IDStr=str(ident)
        else:
            self.m_IDStr=identStr
            if upperCase:
                self.m_IDStr=self.m_IDStr.upper()
        self.m_Readable=readable

    def __str__(self):
        return self.m_IDStr

    def getID(self)->int:
        return self.m_ID

    def getIDStr(self):
        return self.m_IDStr

    def getReadable(self):
        return self.m_Readable

    @classmethod
    def toOptionList(cls,tags:List):
        result="<"
        for i in range(len(tags)):
            if i>0:
                result+="|"
            result+=tags[i]
        result+=">"
        return result