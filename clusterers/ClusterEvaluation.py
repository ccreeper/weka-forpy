from typing import *
from Instances import Instances,Instance
from clusterers.Clusterer import Clusterer
from clusterers.SimpleKMeans import SimpleKMeans
from clusterers.DensityBasedClusterer import DensityBasedClusterer
from Attributes import Attribute
from filters.attribute.Remove import Remove
from filters.Filter import Filter
from Utils import Utils
import copy
import math

class ClusterEvaluation():
    def __init__(self):
        self.m_numClusters=0
        self.m_logL=0
        self.m_classToCluster=None      #type:List[int]

        self.setClusterer(SimpleKMeans())
        self.m_clusteringResult=""
        self.m_clusterAssignments=None      #type:List

    def getNumClusters(self):
        return self.m_numClusters

    def getClusterAssignments(self):
        return self.m_clusterAssignments

    def getClassesToClusters(self):
        return self.m_classToCluster

    def setClusterer(self,clusterer:Clusterer):
        self.m_Clusterer=clusterer

    def evaluateClusterer(self,test:Instances,outputModel:bool):
        i=loglk=unclusteredInstances=0
        cc=self.m_Clusterer.numberOfClusters()
        self.m_numClusters=cc
        instanceStats=[0]*cc
        hasClass=test.classIndex()>=0
        clusterAssignments=[]
        filter=None     #type:Filter

        testRaw=copy.deepcopy(test)
        testRaw.setClassIndex(test.classIndex())

        if hasClass:
            if testRaw.classAttribute().isNumeric():
                raise Exception(unclusteredInstances)
            filter=Remove()
            filter.setAttributeIndices(str(testRaw.classIndex()+1))
            filter.setInvertSelection(False)
            filter.setInputFormat(testRaw)
        for inst in testRaw:
            if filter is not None:
                filter.input(inst)
                filter.batchFinished()
                inst=filter.output()
            cnum=self.m_Clusterer.clusterInstance(inst)
            clusterAssignments.append(cnum)
            if cnum != -1:
                instanceStats[cnum]+=1
        sumNum=sum(instanceStats)
        loglk/=sumNum
        self.m_logL=loglk
        self.m_clusterAssignments=[]
        # for i in clusterAssignments:
        #     print(",",i,end="")
        # print()
        for i in range(len(clusterAssignments)):
            self.m_clusterAssignments.append(clusterAssignments[i])
        numInstFieldWidth=int(math.log(len(clusterAssignments))/math.log(10)+1)
        if outputModel:
            self.m_clusteringResult+=str(self.m_Clusterer)
        self.m_clusteringResult+="Clustered Instances\n\n"
        clustFieldWidth=int((math.log(cc)/math.log(10))+1)
        for i in range(cc):
            if instanceStats[i]>0:
                self.m_clusteringResult+=Utils.doubleToString(i,clustFieldWidth,0)\
                                        +"      "\
                                        +Utils.doubleToString(instanceStats[i],numInstFieldWidth,0)\
                                        +"("+Utils.doubleToString((instanceStats[i]/sumNum*100),3,0)\
                                        +"%)\n"
        if unclusteredInstances > 0:
            self.m_clusteringResult+="\nUnclustered instances : "+str(unclusteredInstances)
        if hasClass:
            self.evaluateClustersWithRespectToClass(test)

    def clusterResultsToString(self):
        return self.m_clusteringResult


    def evaluateClustersWithRespectToClass(self,inst:Instances):
        numClasses=inst.classAttribute().numValues()
        counts=[[0]*numClasses for i in range(self.m_numClusters)]
        clusterTotals=[0]*self.m_numClusters
        best=[0]*(self.m_numClusters+1)
        current=[0]*(self.m_numClusters+1)

        instances=copy.deepcopy(inst)
        instances.setClassIndex(inst.classIndex())
        i=0
        for instance in instances:
            if self.m_clusterAssignments[i]>=0:
                if not instance.classIsMissing():
                    counts[int(self.m_clusterAssignments[i])][int(instance.classValue())]+=1
                    clusterTotals[int(self.m_clusterAssignments[i])]+=1
            i+=1
        numInstances=i
        best[self.m_numClusters]=float('inf')
        self.mapClasses(self.m_numClusters,0,counts,clusterTotals,current,best,0)
        self.m_clusteringResult+="\n\nClass attribute: "+ inst.classAttribute().name() + "\n"
        self.m_clusteringResult+="Classes to Clusters:\n"
        matrixString=self.toMatrixString(counts,clusterTotals,Instances(inst,0))
        self.m_clusteringResult+=matrixString+'\n'
        Cwidth=1+int(math.log(self.m_numClusters)/math.log(10))
        for i in range(self.m_numClusters):
            if clusterTotals[i] > 0 :
                self.m_clusteringResult+="Cluster "+ Utils.doubleToString(i, Cwidth, 0)
                self.m_clusteringResult+=" <-- "
                if best[i] < 0:
                    self.m_clusteringResult+="No class\n"
                else:
                    self.m_clusteringResult+=inst.classAttribute().value(int(best[i]))+'\n'
        self.m_clusteringResult+="\nIncorrectly clustered instances :\t"\
                                  + str(best[self.m_numClusters])\
                                  + "\t"\
                                  + Utils.doubleToString((best[self.m_numClusters] / numInstances * 100.0), 8,4) \
                                  + " %\n"
        self.m_classToCluster=[]
        for i in range(self.m_numClusters):
            self.m_classToCluster[i]=int(best[i])

    def toMatrixString(self,counts:List[List],clusterTotals:List,inst:Instances):
        ms=""
        maxval=0
        for i in range(self.m_numClusters):
            for j in range(len(counts[0])):
                if counts[i][j] > maxval:
                    maxval=counts[i][j]
        Cwidth=1+max(int(math.log(maxval)/math.log(10)),int(math.log(self.m_numClusters)/math.log(10)))
        ms+='\n'
        for i in range(self.m_numClusters):
            if clusterTotals[i]>0:
                ms+=" "+Utils.doubleToString(i,Cwidth,0)
        ms+="  <-- assigned to cluster\n"
        for i in range(len(counts[0])):
            for j in range(self.m_numClusters):
                if clusterTotals[j]>0:
                    ms+=" "+Utils.doubleToString(counts[j][i],Cwidth,0)
            ms+=" | "+inst.classAttribute().value(i)+"\n"
        return ms

    @classmethod
    def mapClasses(cls,numClusters:int,lev:int,counts:List[List],clusterTotals:List,current:List,best:List,error:int):
        if lev == numClusters:
            if error < best[numClusters]:
                best[numClusters] = error
                for i in range(numClusters):
                    best[i]=current[i]
        else:
            if clusterTotals[lev]==0:
                current[lev]=-1
                cls.mapClasses(numClusters,lev+1,counts,clusterTotals,current,best,error)
            else:
                current[lev]=-1
                cls.mapClasses(numClusters,lev+1,counts,clusterTotals,current,best,error+clusterTotals[lev])
            for i in range(len(counts[0])):
                if counts[lev][i]>0:
                    ok=True
                    for j in range(lev):
                        if int(current[j]) == i:
                            ok=False
                            break
                    if ok:
                        current[lev]=i
                        cls.mapClasses(numClusters,lev+1,counts,clusterTotals,current,best,error+clusterTotals[lev]-counts[lev][i])



