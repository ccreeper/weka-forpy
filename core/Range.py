from typing import *
import copy

class Range():
    def __init__(self,rangeList:str=None):
        self.m_Upper=-1
        if rangeList is not None:
            self.setRanges(rangeList)

    def setInvert(self,newSetting:bool):
        self.m_Invert=newSetting

    def setUpper(self,newUpper:int):
        if newUpper >=0:
            self.m_Upper=newUpper
            self.setFlags()

    def getSelection(self):
        if self.m_Upper == -1:
            raise Exception("No upper limit has been specified for range")
        selectIndices=[]
        if self.m_Invert:
            for i in range(self.m_Upper+1):
                if not self.m_SelectFlags[i]:
                    selectIndices.append(i)
        else:
            for item in self.m_RangeStrings:
                start=self.rangeLower(item)
                end=self.rangeUpper(item)
                for i in range(start,end+1):
                    if i>self.m_Upper:
                        break
                    if self.m_SelectFlags[i]:
                        selectIndices.append(i)
        return selectIndices

    def setFlags(self):
        self.m_SelectFlags=[]
        for item in self.m_RangeStrings:
            if not self.isValidRange(item):
                raise Exception("Invalid range list at "+ item)
            start=self.rangeLower(item)
            end=self.rangeUpper(item)
            for i in range(start,end+1):
                if i > self.m_Upper:
                    break
                self.m_SelectFlags[i]=True

    def rangeUpper(self,rangeStr:str):
        try:
            hyphenIndex=rangeStr.index('-')
            return max(self.rangeUpper(rangeStr[:hyphenIndex]),self.rangeUpper(rangeStr[hyphenIndex+1:]))
        except ValueError:
            return self.rangeSingle(rangeStr)

    def rangeLower(self,rangeStr:str):
        try:
            hyphenIndex=rangeStr.index('-')
            return min(self.rangeLower(rangeStr[:hyphenIndex]),self.rangeLower(rangeStr[hyphenIndex+1:]))
        except ValueError:
            return self.rangeSingle(rangeStr)

    def rangeSingle(self,single:str):
        if single.lower() == 'first':
            return 0
        if single.lower() == 'last':
            return self.m_Upper
        index=int(single)-1
        if index<0:
            index=0
        if index>self.m_Upper:
            index=self.m_Upper
        return index

    def isValidRange(self,rangeStr:str):
        if rangeStr is None:
            return False
        try:
            hyphenIndex=rangeStr.index('-')
            if self.isValidRange(rangeStr[:hyphenIndex]) and self.isValidRange(rangeStr[hyphenIndex+1:]):
                return True
            return False
        except ValueError:
            pass
        if rangeStr.lower() == "first":
            return True
        if rangeStr.lower() == "last":
            return True
        try:
            index=int(rangeStr)
            if index>0 and index<=self.m_Upper+1:
                return True
            return False
        except ValueError:
            return False



    def setRanges(self,rangeList:str):
        ranges=[]
        while rangeList != "":
            range=rangeList.strip()
            try:
                commaLoc=rangeList.index(',')
                range=rangeList[:commaLoc]
                range.strip()
                rangeList=rangeList[commaLoc+1:]
                rangeList.strip()
            except ValueError:
                rangeList=""
            if range != "":
                ranges.append(range)
        self.m_RangeStrings=ranges      #type:List[str]
        self.m_SelectFlags=None

    @classmethod
    def indicesToRangeList(cls,indices:List[int]):
        rl=""
        last=-2
        rangeFlag=False
        for i in range(len(indices)):
            if i==0:
                rl+=str(indices[i]+1)
            elif indices[i] == last:
                rangeFlag=True
            else:
                if rangeFlag:
                    rl+='-'+str(last)
                    rangeFlag=False
                rl+=','+str(indices[i]+1)
            last=indices[i]+1
        if rangeFlag:
            rl+='-'+str(last)
        return rl


