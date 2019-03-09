from typing import *
from core.neighboursearch.NearestNeighbourSearch import NearestNeighbourSearch
from Instances import Instances,Instance
from EuclideanDistance import EuclideanDistance
from core.neighboursearch.MyHeap import MyHeap,MyHeapElement
from Utils import Utils

class LinearNNSearch(NearestNeighbourSearch):
    def __init__(self,insts:Instances=None):
        super().__init__(insts)
        self.m_DistanceFunction=EuclideanDistance()
        self.m_SkipIdentical=False
        if insts is not None:
            self.m_DistanceFunction.setInstances(insts)

    def setInstances(self,insts:Instances):
        self.m_Instances=insts
        self.m_DistanceFunction.setInstances(insts)

    def addInstanceInfo(self,ins:Instance):
        if self.m_Instances is not None:
            self.update(ins)


    def update(self,ins:Instance):
        if self.m_Instances is None:
            raise Exception("No instances supplied yet. Cannot update without"+"supplying a set of instances first.")
        self.m_DistanceFunction.update(ins)

    def kNearestNeighbours(self,target:Instance,kNN:int)->Instances:
        if self.m_Stats is not None:
            self.m_Stats.searchStart()
        heap=MyHeap(kNN)
        firstkNN=0
        for i in range(self.m_Instances.numInstances()):
            if target == self.m_Instances.instance(i):
                continue
            if self.m_Stats is not None:
                self.m_Stats.incrPointCount()
            if firstkNN < kNN:
                distance=self.m_DistanceFunction.distance(target,self.m_Instances.instance(i),float("inf"),self.m_Stats)
                if distance == 0 and self.m_SkipIdentical and i < self.m_Instances.numInstances()-1:
                    continue
                heap.put(i,distance)
                firstkNN+=1
            else:
                temp=heap.peek()
                distance=self.m_DistanceFunction.distance(target,self.m_Instances.instance(i),temp.distance,self.m_Stats)
                if distance == 0 and self.m_SkipIdentical:
                    continue
                if distance < temp.distance:
                    heap.putBySubstitute(i,distance)
                elif distance == temp.distance:
                    heap.putKthNearest(i,distance)
        neighbours=Instances(self.m_Instances,heap.size()+heap.noOfKthNearest())
        self.m_Distances=[0]*(heap.size()+heap.noOfKthNearest())
        indices=[0]*(heap.size()+heap.noOfKthNearest())
        i=1
        while heap.noOfKthNearest() > 0:
            h=heap.getKthNearest()
            indices[len(indices)-i]=h.index
            self.m_Distances[len(indices) - i]=h.distance
            i+=1
        while heap.size() > 0:
            h=heap.get()
            indices[len(indices)-i]=h.index
            self.m_Distances[len(indices) - i]=h.distance
            i+=1
        self.m_DistanceFunction.postProcessDistances(self.m_Distances)
        for k in range(len(indices)):
            neighbours.add(self.m_Instances.instance(indices[k]))
        if self.m_Stats is not None:
            self.m_Stats.searchStart()
        return neighbours

    def getDistances(self):
        if self.m_Distances is None:
            raise Exception("No distances available. Please call either "+
                          "kNearestNeighbours or nearestNeighbours first.")
        return self.m_Distances
