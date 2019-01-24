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