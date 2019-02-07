import math
from functools import partial
from typing import *


#TODO  整合
class Utils():
    #debug模式
    DEBUG=True
    equal=partial(math.isclose,rel_tol=1e-6)

    @classmethod
    def padLeft(cls,string:str,length:int):
        return ("{0:>"+str(length)+"."+str(length)+"}").format(string)

    @classmethod
    def isMissingValue(cls,value):
        return math.isnan(value)

    @classmethod
    def missingValue(cls):
        return float("nan")

    @classmethod
    def doubleToString(cls,number:float,len:int):
        return str(round(number,len))

    @classmethod
    def initialIndex(cls,size:int):
        index=[]
        for i in range(size):
            index.append(i)
        return index

    @classmethod
    def sortWithNoMissingValues(cls,array:List[float])->List[int]:
        index=cls.initialIndex(len(array))
        if len(array)>1:
            cls.quickSort(array,index,0,len(array)-1)
        return index

    @classmethod
    def quickSort(cls,array:List[float],index:List[int],left:int,right:int):
        diff=right-left
        if diff == 0:
            return
        elif diff == 1:
            cls.conditionalSwap(array,index,left,right)
            return
        elif diff == 2:
            cls.conditionalSwap(array,index,left,left+1)
            cls.conditionalSwap(array,index,left,right)
            cls.conditionalSwap(array,index,left+1,right)
            return
        else:
            pivotLocation=cls.sortLeftRightAndCenter(array,index,left,right)
            cls.swap(index,pivotLocation,right-1)
            center=cls.partition(array,index,left,right,array[index[right-1]])
            cls.swap(index,center,right-1)

            cls.quickSort(array,index,left,center-1)
            cls.quickSort(array,index,center+1,right)


    @classmethod
    def conditionalSwap(cls,array:List[float],index:List[int],left:int,right:int):
        if array[index[left]]>array[index[right]]:
            cls.swap(index,left,right)

    @classmethod
    def sortLeftRightAndCenter(cls,array:List[float],index:List[int],left:int,right:int):
        mid=int((left+right)/2)
        cls.conditionalSwap(array,index,left,mid)
        cls.conditionalSwap(array,index,left,right)
        cls.conditionalSwap(array,index,mid,right)
        return mid

    @classmethod
    def swap(cls,index:List[int],left:int,right:int):
        tmp=index[left]
        index[left]=index[right]
        index[right]=tmp

    @classmethod
    def partition(cls,array:List[float],index:List[int],l:int,r:int,pivot:float):
        r-=1
        while True:
            l+=1
            while array[index[l]] < pivot:pass
            r-=1
            while array[index[r]] > pivot:pass
            if l>=r:
                return l
            cls.swap(index,l,r)

    @classmethod
    def limit(cls,number,limit):
        if number<limit:
            return limit
        else:
            return number

    @classmethod
    def debugOut(cls,*args):
        if cls.DEBUG:
            string=""
            for i in args:
                string+=" "+str(i)
            print(string)

    @classmethod
    def getOption(cls,flag:str,options:List[str]):
        i=cls.getOptionPos(flag,options)
        if i>-1:
            if options[i] == '-'+flag:
                options[i]=""
                newString=options[i+1]
                options[i+1]=""
                return newString
            if options[i][1]=='-':
                return ""
        return ""

    @classmethod
    def getOptionPos(cls,flag:str,options:List[str]):
        if options is None:
            return -1
        for i in range(len(options)):
            if len(options[i])>0 and options[i][0]=="-":
                try:
                    float(options[i])
                except ValueError:
                    if options[i] == '-'+flag:
                        return i
                    if options[i][1] == '-':
                        return -1
        return -1

    @classmethod
    def unbackQuoteChars(cls,string:str):
        charsFind=("\\\\","\\'","\\t","\\n","\\r","\\\"","\\%","\\u001E")
        charsReplace=('\\','\'','\t','\n','\r','"','%','\u001E')
        return cls.replaceStrings(string,charsFind,charsReplace)

    @classmethod
    def backQuoteChars(cls,string:str):
        charsFind=['\\', '\'', '\t', '\n', '\r', '"', '%', '\u001E']
        charsReplace=["\\\\", "\\'", "\\t", "\\n", "\\r", "\\\"", "\\%", "\\u001E"]
        for i in range(len(charsFind)):
            try:
                index=string.index(charsFind[i])
                newStr = ""
                while True:
                    if index>0:
                        newStr+=string[0:index]
                    newStr+=charsReplace[i]
                    if (index+1)<len(string):
                        string=string[index+1:]
                    else:
                        string=""
                    try:
                        index=string.index(charsFind[i])
                    except ValueError:
                        newStr+=string
                        string=newStr
                        break
            except ValueError:
                continue

    @classmethod
    def replaceStrings(cls,s:str,charsFind:List[str],charsReplace:List[str]):
        pos=[0]*len(charsFind)
        string=s
        newString=""
        while len(string)>0:
            curPos=len(string)
            index=-1
            for i in range(len(pos)):
                try:
                    pos[i]=string.index(charsFind[i])
                    if pos[i]<curPos:
                        index=i
                        curPos=pos[i]
                except ValueError:
                    index=-1
            if index==-1:
                newString+=string
                string=""
            else:
                newString+=string[0:pos[index]]
                newString+=charsReplace[index]
                string=string[pos[index]+len(charsFind[index]):]

        return newString

    @classmethod
    def sort(cls,arr:List):
        index=cls.initialIndex(len(arr))
        newIndex=[0]*len(arr)
        helpIndex=[]
        numEqual=0
        cls.quickSort(arr,index,0,len(arr)-1)
        i=0
        while i<len(index):
            numEqual=1
            for j in range(i+1,len(index)):
                if arr[index[i]]!=arr[index[j]]:
                    break
                numEqual+=1
            if numEqual>1:
                helpIndex=[]
                for j in range(numEqual):
                    helpIndex.append(i+j)
                index.sort()
                cls.quickSort(index,helpIndex,0,numEqual-1)
                for j in range(numEqual):
                    newIndex[i+j]=index[helpIndex[j]]
                i+=numEqual
            else:
                newIndex[i]=index[i]
                i+=1
        return newIndex


    @classmethod
    def initialIndex(cls,size:int):
        index=[]
        for i in range(size):
            index.append(i)
        return index
