from typing import *



class MyHeapElement():
    def __init__(self, i: int, d: float):
        self.distance = d
        self.index = i

class MyHeap():
    def __init__(self,maxSize:int):
        self.m_KthNearestSize=0
        if maxSize%2 == 0:
            maxSize+=1
        self.m_heap=[None]*(maxSize+1)      #type:List[MyHeapElement]
        self.m_KthNearest=None        #type:List[MyHeapElement]
        self.m_heap[0]=MyHeapElement(0,0)

    def size(self):
        return self.m_heap[0].index

    def peek(self)->MyHeapElement:
        return self.m_heap[1]

    def getKthNearest(self)->MyHeapElement:
        if self.m_KthNearestSize == 0:
            return None
        self.m_KthNearestSize-=1
        return self.m_KthNearest[self.m_KthNearestSize]

    def noOfKthNearest(self):
        return self.m_KthNearestSize

    def get(self)->MyHeapElement:
        if self.m_heap[0].index == 0:
            raise Exception("No elements present in the heap")
        r=self.m_heap[1]
        self.m_heap[1]=self.m_heap[self.m_heap[0].index]
        self.m_heap[0].index-=1
        self.downheap()
        return r

    def put(self, i:int, d:float):
        if self.m_heap[0].index+1 > len(self.m_heap)-1:
            raise Exception("the number of elements cannot exceed the "
                            + "initially set maximum limit")
        self.m_heap[0].index+=1
        self.m_heap[self.m_heap[0].index]=MyHeapElement(i, d)
        self.upheap()

    def putBySubstitute(self,i:int,j:float):
        head=self.get()
        self.put(i,j)
        if head.distance == self.m_heap[1].distance:
            self.putKthNearest(head.index,head.distance)
        elif head.distance > self.m_heap[1].distance:
            self.m_KthNearest=None
            self.m_KthNearestSize=0
        elif head.distance < self.m_heap[1].distance:
            raise Exception("The substituted element is smaller than the "
                          + "head element. put() should have been called "
                          + "in place of putBySubstitute()")

    def putKthNearest(self,i:int,j:float):
        if self.m_KthNearest is None:
            self.m_KthNearest=[]
        self.m_KthNearestSize+=1
        self.m_KthNearest.append(MyHeapElement(i,j))

    def upheap(self):
        i=self.m_heap[0].index
        while i>1 and self.m_heap[i].distance > self.m_heap[i//2].distance:
            temp=self.m_heap[i]
            self.m_heap[i]=self.m_heap[i//2]
            i//=2
            self.m_heap[i]=temp


    def downheap(self):
        i=1
        while (2*i <= self.m_heap[0].index and self.m_heap[i].distance < self.m_heap[2*i].distance)\
            or ((2*i+1) <= self.m_heap[0].index and self.m_heap[i].distance < self.m_heap[2*i+1].distance):
            if (2*i+1) <= self.m_heap[0].index:
                if self.m_heap[2*i].distance > self.m_heap[2*i+1].distance:
                    temp=self.m_heap[i]
                    self.m_heap[i]=self.m_heap[2*i]
                    i*=2
                    self.m_heap[i]=temp
                else:
                    temp=self.m_heap[i]
                    self.m_heap[i]=self.m_heap[2*i+1]
                    i=2*i+1
                    self.m_heap[i]=temp
            else:
                temp=self.m_heap[i]
                self.m_heap[i]=self.m_heap[2*i]
                i*=2
                self.m_heap[i]=temp

