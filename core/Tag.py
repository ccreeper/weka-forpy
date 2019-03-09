from typing import *

class Tag():
    @overload
    def __init__(self):
        self.m_IDStr=None
        self.m_Readable=None
        self.m_ID=None
    @overload
    def __init__(self,ident:int,readable:str):...
    @overload
    def __init__(self,ident:int,identStr:str,readable:str):...
    @overload
    def __init__(self,ident:int,identStr:str,readable:str,upperCase:bool):...

    def __init__(self,a0=None,a1=None,a2=None,a3=None):
        if a0 is None and a1 is None and a2 is None and a3 is None:
            self.__init__(0,"A new tag","A new tag",True)
        elif isinstance(a0,int) and isinstance(a1,str) and a2 is None and a3 is None:
            self.__init__(a0,"",a1)
        elif isinstance(a0,int) and isinstance(a1,str) and isinstance(a2,str) and a3 is None:
            self.__init__(a0,a1,a2,True)
        elif isinstance(a0,int) and isinstance(a1,str) and isinstance(a2,str) and isinstance(a3,bool):
            self.m_ID=a0
            if len(a1) == 0:
                self.m_IDStr=str(a0)
            else:
                self.m_IDStr=a1
                if a3:
                    self.m_IDStr=a1.upper()
            self.m_Readable=a3


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