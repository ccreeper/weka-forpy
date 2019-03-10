import math
from functools import partial
from typing import *
from Statistics import Statistics
import importlib


#TODO  整合
class Utils():
    #debug模式
    DEBUG=True
    equal=partial(math.isclose,rel_tol=1e-6)
    MAX_INT_FOR_CACHE_PLUS_ONE=10000
    INT_N_LOG_N_CACHE=[]

    for i in range(MAX_INT_FOR_CACHE_PLUS_ONE):
        INT_N_LOG_N_CACHE.append(i*math.log(i))

    @classmethod
    def padLeft(cls,string:str,length:int):
        return ("{0:>"+str(length)+"."+str(length)+"}").format(string)

    @classmethod
    def isMissingValue(cls,value):
        return math.isnan(value)

    @classmethod
    def gr(cls,a:float,b:float):
        return a-b>1e-6

    @classmethod
    def normalize(cls,numbers:List,sum:float):
        for i in range(len(numbers)):
            numbers[i]/=sum

    @classmethod
    def maxIndex(cls,numList:List):
        maximun=0
        maxIndex=0
        for i in range(len(numList)):
            if i==0 or numList[i]>maximun:
                maxIndex=i
                maximun=numList[i]
        return maxIndex

    @classmethod
    def missingValue(cls):
        return float("nan")

    @classmethod
    def roundDouble(cls,value:float,afterDecimalPoint:int):
        mask=10**afterDecimalPoint
        return round(value*mask)/mask

    @classmethod
    def doubleToString(cls, number:float, a0:int,a1=None):
        if a1 is None:
            return str(round(number, a0))
        else:
            tempString=cls.doubleToString(number,a1)
            if a1 >= a0:
                return tempString
            result=[]
            for i in range(a0):
                result.append(" ")
            if a1 > 0 :
                try:
                    dotPosition=tempString.index('.')
                    result[a0-a1-1]='.'
                except ValueError:
                    dotPosition = len(tempString)
            else:
                dotPosition=len(tempString)
            offset=a0-a1-dotPosition
            if a1 > 0:
                offset-=1
            if offset<0:
                return tempString
            for i in range(dotPosition):
                result[offset+i]=tempString[i]
            for i in range(dotPosition+1,len(tempString)):
                result[offset+i]=tempString[i]
            return "".join(result)


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
    def addErrs(cls,N:float,e:float,CF:float):
        if CF > 0.5:
            return 0
        if e < 1:
            base=N*(1-CF**1/N)
            if e == 0:
                return base
            return base+e*(cls.addErrs(N,1,CF)-base)
        if e+0.5 >= N:
            return max(N-e,0)
        z=Statistics.normalInverse(1-CF)
        f=(e+0.5)/N
        r=(f+(z*z)/(2*N)+z*math.sqrt(f/N-f*f/N+z*z/(4*N*N)))/(1+z*z/N)
        return r*N-e

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
    def quote(cls,string:str):
        quote=False
        if '\n' in string or '\r' in string or "'" in string or '"' in string or '\\' in string or \
            '\t' in string or '%' in string or '\u001E' in string :
            string=cls.backQuoteChars(string)
            quote=True
        if quote or '{' in string or '}' in string or ',' in string or string=="?" or ' ' in string or string == "":
            string="'"+string+"'"
        return string

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
            while array[index[l]] < pivot:
                l+=1
            r-=1
            while array[index[r]] > pivot:
                r-=1
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
    def lnFunc(cls,num:float):
        if num <= 0:
            return 0
        if num < cls.MAX_INT_FOR_CACHE_PLUS_ONE:
            n=int(num)
            if n == num:
                return cls.INT_N_LOG_N_CACHE[n]
        return num*math.log(num)


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
        charsFind=["\\\\","\\'","\\t","\\n","\\r","\\\"","\\%","\\u001E"]
        charsReplace=['\\','\'','\t','\n','\r','"','%','\u001E']
        return cls.replaceStrings(string,charsFind,charsReplace)

    @classmethod
    def backQuoteChars(cls,string:str)->str:
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
        return string

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
    def sortDouble(cls,arr:List):
        index=cls.initialIndex(len(arr))
        if len(arr)>1:
            arr=arr[:]
            cls.replaceMissingWithMAX_VALUE(arr)
            cls.quickSort(arr,index,0,len(arr)-1)
        return index

    @classmethod
    def sort(cls,arr:List)->List:
        index=cls.initialIndex(len(arr))
        newIndex=[0]*len(arr)
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

    @classmethod
    def loadClassForName(cls,classname:str)->type:
        imp = importlib.import_module(classname)
        try:
            cla = getattr(imp, classname.split('.')[-1])
            return cla
        except BaseException:
            return None

    @classmethod
    def joinOptions(cls,optionArray:List[str]):
        optionString=""
        for element in optionArray:
            if element == "":
                continue
            escape=False
            for i in range(len(element)):
                if element[i].isspace() or element[i] == '"' or element[i] == "'":
                    escape=True
                    break
            if escape:
                optionString+='"'+cls.backQuoteChars(element)+'"'
            else:
                optionString+=element
            optionString+=" "
        return optionString.strip()

    @classmethod
    def splitOptions(cls,quotedOptionString:str,toReplace:List[str],replacements:List[str])->List[str]:
        optionsVec=[]
        string=quotedOptionString
        while True:
            i=0
            while i < len(string) and string[i].isspace():
                i+=1
            string=string[i:]
            if len(string) == 0:
                break
            if string[0] == '"':
                i=1
                while i<len(string):
                    if string[i] == string[0]:
                        break
                    if string[i] == '\\':
                        i+=1
                        if i >= len(string):
                            raise Exception("String should not finish with \\")
                    i+=1
                if i >= len(string):
                    raise Exception("Quote parse error.")
                optStr=string[1:i]
                if toReplace is not None and replacements is not None:
                    optStr=cls.replaceStrings(optStr,toReplace,replacements)
                else:
                    optStr=cls.unbackQuoteChars(optStr)
                optionsVec.append(optStr)
                string=string[i+1:]
            else:
                i=0
                while i<len(string) and not string[i].isspace():
                    i+=1
                optStr=string[0:i]
                optionsVec.append(optStr)
                string=string[i:]
        options=[""]*len(optionsVec)
        for i in range(len(optionsVec)):
            options[i]=optionsVec[i]
        return options

    @classmethod
    def log2(cls,a):
        return math.log(a)/math.log(2)

    @classmethod
    def replaceMissingWithMAX_VALUE(cls,array:List):
        for i in range(len(array)):
            if cls.isMissingValue(array[i]):
                array[i]=float("inf")

    @classmethod
    def stableSort(cls,array:List):
        index=cls.initialIndex(len(array))
        if len(array) > 1:
            newIndex=[0]*len(array)
            array=array[:]
            cls.replaceMissingWithMAX_VALUE(array)
            cls.quickSort(array,index,0,len(array)-1)
            i=0
            while i<len(index):
                numEqual=1
                for j in range(i+1,len(index)):
                    if array[index[i]] == array[index[j]]:
                        break
                    numEqual+=1
                if numEqual > 1:
                    helpIndex=[0]*numEqual
                    for j in range(numEqual):
                        helpIndex[j]=i+j
                    cls.quickSort(index,helpIndex,0,numEqual-1)
                    for j in range(numEqual):
                        newIndex[i+j]=index[helpIndex[j]]
                    i+=numEqual
                else:
                    newIndex[i]=index[i]
                    i+=1
            return newIndex
        return index

    @classmethod
    def division(cls,numerator,denominator):
        if denominator == 0 and numerator == 0:
            return float('nan')
        elif denominator == 0 and numerator > 0:
            return float('inf')
        elif denominator == 0 and numerator < 0:
            return float('-inf')
        return numerator/denominator