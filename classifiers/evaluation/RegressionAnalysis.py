from typing import *
from Instances import Instances,Instance
from Attributes import Attribute
import numpy as np
import math

def calculateRSquared(data:Instances,ssr:float):
    yMean=data.meanOrMode(data.classIndex())
    tss=0
    for i in range(data.numInstances()):
        tss+=(data.instance(i).value(data.classIndex())-yMean)*\
             (data.instance(i).value(data.classIndex())-yMean)
    rsq=1-ssr/tss
    return rsq

def calculateAdjRSquared(rsq:float,n:int,k:int):
    if n < 1or k < 2or n == k:
        return float('nan')
    return 1-((1-rsq)*(n-1)/(n-k))

def calculateFStat(rsq:float,n:int,k:int):
    if n < 1 or k < 2 or n == k:
        return float('nan')
    numerator=rsq/(k-1)
    denominator=(1-rsq)/(n-k)
    return numerator/denominator

def calculateStdErrorOfCoef(data:Instances,selected:List[bool],ssr:float,n:int,k:int):
    array=[[0]*k for i in range(n)]
    column=0
    for j in range(data.numAttributes()):
        if data.classIndex() != j and selected[j]:
            for i in range(n):
                array[i][column]=data.instance(i).value(j)
            column+=1
    for i in range(n):
        array[i][k-1]=1
    X=np.array(array)
    XtX=np.dot(X.T,X)
    inverse=np.linalg.pinv(XtX)
    mse=ssr/(n-k)
    cov=mse*inverse
    result=[]
    for i in range(k):
        result.append(math.sqrt(cov[i][i]))
    return result

def calculateTStats(coef:List[float],stderror:List[float],k:int):
    result=[]
    for i in range(k):
        result.append(coef[i]/stderror[i])
    return result
