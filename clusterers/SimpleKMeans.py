from typing import *
from Capabilities import Capabilities,CapabilityEnum
from clusterers.RandomizableClusterer import RandomizableClusterer
from Instances import Instances,Instance
from filters.attribute.ReplaceMissingValues import ReplaceMissingValues
from filters.Filter import Filter
from EuclideanDistance import EuclideanDistance
from Utils import Utils
from classifiers.rules.DecisionTableHashKey import DecisionTableHashKey
import math
import random

class SimpleKMeans(RandomizableClusterer):
    propertyList = RandomizableClusterer.propertyList[:]
    methodList = RandomizableClusterer.methodList[:]
    propertyList.extend(['NumClusters','DontReplaceMissing'])
    def __init__(self):
        super().__init__()
        self.NumClusters=2
        self.DontReplaceMissing=False
        self.m_MaxIterations=500
        self.m_Iterations=0
        self.m_PreserveOrder=False
        self.m_FastDistanceCalc=False
        self.m_SeedDefault=10
        self.m_speedUpDistanceCompWithCanopies=False
        self.m_maxCanopyCandidates=100
        self.m_minClusterDensity=2
        self.m_periodicPruningRate=10000
        self.setSeed(self.m_SeedDefault)
        self.m_ClusterNominalCounts=None        #type:List[List[List[float]]]
        self.m_ClusterMissingCounts=None        #type:List[List[float]]
        self.m_FullMeansOrMediansOrModes=None   #type:List[float]
        self.m_FullStdDevs=None #type:List[float]
        self.m_FullNominalCounts=None       #type:List[List[float]]
        self.m_FullMissingCounts=None       #type:List[float]
        self.m_ClusterCentroids=None        #type:Instances
        self.m_initialStartPoints=None      #type:Instances
        self.m_executionSlots=1
        self.m_ClusterSizes=None        #type:List[float]
        self.m_squaredErrors=None       #type:List[float]
        self.m_DistanceFunction=EuclideanDistance()

    def __str__(self):
        if self.m_ClusterCentroids is None:
            return "No clusterer built yet!"
        maxAttWidth=0
        maxWidth=0
        containsNumberic=False
        for i in range(self.NumClusters):
            for j in range(self.m_ClusterCentroids.numAttributes()):
                if len(self.m_ClusterCentroids.attribute(j).name())>maxAttWidth:
                    maxAttWidth=len(self.m_ClusterCentroids.attribute(j).name())
                if self.m_ClusterCentroids.attribute(j).isNumeric():
                    containsNumberic=True
                    width=math.log(math.fabs(self.m_ClusterCentroids.instance(i).value(j)))/math.log(10)
                    if width<0:
                        width=1
                    width+=6
                    if int(width) > maxWidth:
                        maxWidth=int(width)
        for i in range(self.m_ClusterCentroids.numAttributes()):
            if self.m_ClusterCentroids.attribute(i).isNominal():
                a=self.m_ClusterCentroids.attribute(i)
                for j in range(self.m_ClusterCentroids.numInstances()):
                    val=a.value(int(self.m_ClusterCentroids.instance(j).value(i)))
                    if len(val)>maxWidth:
                        maxWidth=len(val)
                for j in range(a.numValues()):
                    val=a.value(j)+" "
                    if len(val)>maxAttWidth:
                        maxAttWidth=len(val)
        for m_ClusterSize in self.m_ClusterSizes:
            size="("+str(m_ClusterSize)+")"
            if len(size)>maxWidth:
                maxWidth=len(size)
        plusMinus="+/-"
        maxAttWidth+=2
        if maxAttWidth<len("Attribute")+2:
            maxAttWidth=len("Attribute")+2
        if maxWidth<len("Full Data"):
            maxWidth=len("Full Data")+1
        if maxWidth<len("missing"):
            maxWidth=len("missing")+1
        temp="\nkMeans\n======\n"
        temp+="\nNumber of iterations: " + str(self.m_Iterations)
        if not self.m_FastDistanceCalc:
            temp+='\n'
            temp+="Within cluster sum of squared errors: "+ str(sum(self.m_squaredErrors))
        temp+="\n\nInitial starting points (random):\n"
        temp+='\n'
        for i in range(self.m_initialStartPoints.numInstances()):
            temp+="Cluster " + str(i) + ": " + str(self.m_initialStartPoints.instance(i))+"\n"
        temp+="\nMissing values globally replaced with mean/mode"
        temp+="\n\nFinal cluster centroids:\n"
        temp+=self.pad("Cluster#", " ", (maxAttWidth + (maxWidth * 2 + 2))- len("Cluster#"), True)
        temp+='\n'
        temp+=self.pad("Attribute", " ", maxAttWidth - len("Attribute"), False)
        temp+=self.pad("Full Data", " ", maxWidth + 1 - len("Full Data"), True)
        for i in range(self.NumClusters):
            clustNum=str(i)
            temp+=self.pad(clustNum, " ", maxWidth + 1 - len(clustNum), True)
        temp+='\n'
        cSize="(" + str(sum(self.m_ClusterSizes)) + ")"
        temp+=self.pad(cSize, " ", maxAttWidth + maxWidth + 1 - len(cSize),True)
        for i in range(self.NumClusters):
            cSize="(" + str(self.m_ClusterSizes[i]) + ")"
            temp+=self.pad(cSize, " ", maxWidth + 1 - len(cSize), True)
        temp+='\n'
        temp+=self.pad("", "=",maxAttWidth+ (maxWidth * (self.m_ClusterCentroids.numInstances() + 1)
                    + self.m_ClusterCentroids.numInstances() + 1), True)
        temp+='\n'
        for i in range(self.m_ClusterCentroids.numAttributes()):
            attName=self.m_ClusterCentroids.attribute(i).name()
            temp+=attName
            for j in range(maxAttWidth-len(attName)):
                temp+=" "
            if self.m_ClusterCentroids.attribute(i).isNominal():
                if self.m_FullMeansOrMediansOrModes[i] == -1:
                    valMeanMode=self.pad("missing", " ", maxWidth + 1 - len("missing"), True)
                else:
                    strVal=self.m_ClusterCentroids.attribute(i).value(int(self.m_FullMeansOrMediansOrModes[i]))
                    valMeanMode=self.pad(strVal," ",maxWidth+1-len(strVal),True)
            else:
                if math.isnan(self.m_FullMeansOrMediansOrModes[i]):
                    valMeanMode=self.pad("missing", " ", maxWidth + 1 - len("missing"), True)
                else:
                    strVal=Utils.doubleToString(self.m_FullMeansOrMediansOrModes[i],maxWidth,4).strip()
                    valMeanMode=self.pad(strVal," ",maxWidth+1-len(strVal),True)
            temp+=valMeanMode
            for j in range(self.NumClusters):
                if self.m_ClusterCentroids.attribute(i).isNominal():
                    if self.m_ClusterCentroids.instance(j).isMissing(i):
                        valMeanMode=self.pad("missing", " ", maxWidth + 1 - len("missing"), True)
                    else:
                        strVal=self.m_ClusterCentroids.attribute(i).value(int(self.m_ClusterCentroids.instance(j).value(i)))
                        valMeanMode=self.pad(strVal," ",maxWidth+1-len(strVal),True)
                else:
                    if self.m_ClusterCentroids.instance(j).isMissing(i):
                        valMeanMode=self.pad("missing", " ", maxWidth + 1 - len("missing"), True)
                    else:
                        strVal=Utils.doubleToString(self.m_ClusterCentroids.instance(j).value(i),maxWidth,4).strip()
                        valMeanMode=self.pad(strVal," ",maxWidth+1-len(strVal),True)
                temp+=valMeanMode
            temp+='\n'
        temp+='\n\n'
        return temp

    def clusterInstance(self,instance:Instance):
        self.m_ReplaceMissingFilter.input(instance)
        self.m_ReplaceMissingFilter.batchFinished()
        inst=self.m_ReplaceMissingFilter.output()
        return self.clusterProcessedInstance(inst,False,True)

    def pad(self,source:str,padChar:str,length:int,leftPad:bool):
        temp=""
        if leftPad:
            for i in range(length):
                temp+=padChar
            temp+=source
        else:
            temp+=source
            for i in range(length):
                temp+=padChar
        return temp


    def getCapabilities(self)->Capabilities:
        result=super().getCapabilities()
        result.disableAll()
        result.enable(CapabilityEnum.NO_CLASS)
        result.enable(CapabilityEnum.NOMINAL_ATTRIBUTES)
        result.enable(CapabilityEnum.NUMERIC_ATTRIBUTES)
        result.enable(CapabilityEnum.MISSING_VALUES)
        return result

    def buildClusterer(self,data:Instances):
        self.getCapabilities().testWithFail(data)
        self.m_Iterations=0
        self.m_ReplaceMissingFilter=ReplaceMissingValues()
        instances=Instances(data)

        instances.setClassIndex(-1)

        self.m_ReplaceMissingFilter.setInputFormat(instances)
        instances=Filter.useFilter(instances,self.m_ReplaceMissingFilter)

        self.m_ClusterNominalCounts=[[[] for i in range(instances.numAttributes())] for j in range(self.NumClusters)]
        self.m_ClusterMissingCounts=[[0]*instances.numAttributes() for  i in range(self.NumClusters)]

        self.m_FullMeansOrMediansOrModes=self.moveCentroid(0,instances,True,False)
        self.m_FullMissingCounts=self.m_ClusterMissingCounts[0]
        self.m_FullNominalCounts=self.m_ClusterNominalCounts[0]
        sumofWeights=instances.sumOfWeight()
        for i in range(instances.numAttributes()):
            if instances.attribute(i).isNumeric():
                if self.m_FullMissingCounts[i] == sumofWeights:
                    self.m_FullMeansOrMediansOrModes[i]=float('nan')
            else:
                if self.m_FullMissingCounts[i]>self.m_FullNominalCounts[i][Utils.maxIndex(self.m_FullNominalCounts[i])]:
                    self.m_FullMeansOrMediansOrModes[i]=-1
        self.m_ClusterCentroids=Instances(instances,self.NumClusters)
        clusterAssignments=[0]*instances.numInstances()
        self.m_DistanceFunction.setInstances(instances)
        random.seed(self.getSeed())
        initC=dict()        #type:Dict[DecisionTableHashKey,int]
        initInstances=instances

        for j in range(initInstances.numInstances(),-1,-1):
            instIndex=random.randint(0,j)
            hk=DecisionTableHashKey(initInstances.instance(instIndex),initInstances.numAttributes(),True)
            if hk not in initC:
                self.m_ClusterCentroids.add(initInstances.instance(instIndex))
                initC.update({hk:None})
            initInstances.swap(j,instIndex)
            if self.m_ClusterCentroids.numInstances() == self.NumClusters:
                break
        self.m_initialStartPoints=Instances(self.m_ClusterCentroids)
        self.NumClusters=self.m_ClusterCentroids.numInstances()
        initInstances=None
        converged=False
        tempI=[]    #type:List[Instances]
        self.m_squaredErrors=[]
        self.m_ClusterNominalCounts=[[[] for i in range(instances.numAttributes())] for j in range(self.NumClusters)]
        self.m_ClusterMissingCounts=[[0]*instances.numAttributes() for  i in range(self.NumClusters)]
        while not converged:
            emptyClusterCount=0
            self.m_Iterations+=1
            converged=True
            if self.m_executionSlots<=1 or instances.numInstances() <2*self.m_executionSlots:
                for i in range(instances.numInstances()):
                    toCluster=instances.instance(i)
                    newC=self.clusterProcessedInstance(toCluster,False,True)
                    if newC != clusterAssignments[i]:
                        converged=False
                    clusterAssignments[i]=newC
            self.m_ClusterCentroids=Instances(instances,self.NumClusters)
            for i in range(self.NumClusters):
                tempI[i]=Instances(instances,0)
            for i in range(instances.numInstances()):
                tempI[clusterAssignments[i]].add(instances.instance(i))
            for i in range(self.NumClusters):
                if tempI[i].numInstances() == 0:
                    emptyClusterCount+=1
                else:
                    self.moveCentroid(i,tempI[i],True,True)
            if self.m_Iterations == self.m_MaxIterations:
                converged=True
            if emptyClusterCount>0:
                self.NumClusters-=emptyClusterCount
                if converged:
                    t=[None]*self.NumClusters   #type:List[Instances]
                    index=0
                    for k in range(len(tempI)):
                        if tempI[k].numInstances()>0:
                            t[index]=tempI[k]
                            for i in range(tempI[k].numAttributes()):
                                self.m_ClusterNominalCounts[index][i]=self.m_ClusterNominalCounts[k][i]
                            index+=1
                    tempI=t
                else:
                    tempI=[None]*self.NumClusters
            if not converged:
                self.m_ClusterNominalCounts=[[[] for i in range(instances.numAttributes())] for j in range(self.NumClusters)]
        if not self.m_FastDistanceCalc:
            for i in range(instances.numInstances()):
                self.clusterProcessedInstance(instances.instance(i),True,False)
        self.m_ClusterSizes=[]
        for i in range(self.NumClusters):
            self.m_ClusterSizes.append(tempI[i].sumOfWeight())
        self.m_DistanceFunction.clean()

    def clusterProcessedInstance(self,instance:Instance,updateErrors:bool,useFastDistCalc:bool):
        minDist=float('inf')
        bestCluster=0
        for i in range(self.NumClusters):
            if useFastDistCalc:
                dist=self.m_DistanceFunction.distance(instance,self.m_ClusterCentroids.instance(i),minDist)
            else:
                dist=self.m_DistanceFunction.distance(instance,self.m_ClusterCentroids.instance(i))
            if dist<minDist:
                minDist=dist
                bestCluster=i
        if updateErrors:
            minDist*=minDist*instance.weight()
            self.m_squaredErrors[bestCluster]+=minDist
        return bestCluster

    def moveCentroid(self,centroidIndex:int,members:Instances,updateClusterInfo:bool,addToCentroidInstances:bool):
        vals=[0]*members.numAttributes()
        nominalDists=[[] for i in range(members.numAttributes())]
        weightMissing=[0]*members.numAttributes()
        weightNonMissing=[0]*members.numAttributes()
        for j in range(members.numAttributes()):
            if members.attribute(j).isNominal():
                nominalDists[j]=[0]*members.attribute(j).numValues()
        for inst in members:
            for j in range(members.numAttributes()):
                if inst.isMissing(j):
                    weightMissing[j]+=inst.weight()
                else:
                    weightNonMissing[j]+=inst.weight()
                    if members.attribute(j).isNumeric():
                        vals[j]+=inst.weight()*inst.value(j)
                    else:
                        nominalDists[j][int(inst.value(j))]+=inst.weight()
        for j in range(members.numAttributes()):
            if members.attribute(j).isNumeric():
                if weightNonMissing[j]>0:
                    vals[j]/=weightNonMissing[j]
                else:
                    vals[j]=Utils.missingValue()
            else:
                max=float('-inf')
                maxIndex=-1
                for i in range(len(nominalDists[j])):
                    if nominalDists[j][i]>max:
                        max=nominalDists[j][i]
                        maxIndex=i
                    if max < weightMissing[j]:
                        vals[j]=Utils.missingValue()
                    else:
                        vals[j]=maxIndex
            if updateClusterInfo:
                for j in range(members.numAttributes()):
                    self.m_ClusterMissingCounts[centroidIndex][j]=weightMissing[j]
                    self.m_ClusterNominalCounts[centroidIndex][j]=nominalDists[j]
            if addToCentroidInstances:
                self.m_ClusterCentroids.add(Instance(1,vals))

            return vals
