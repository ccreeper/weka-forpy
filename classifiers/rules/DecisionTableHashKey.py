import math

from core.Instances import Instance


class DecisionTableHashKey():
    def __init__(self, t, numAtts:int, ignoreClass:bool):
        if isinstance(t, Instance):
            cindex=t.classIndex()
            key=-999
            attributes=[0]*numAtts
            missing=[]
            for i in range(numAtts):
                if i == cindex and not ignoreClass:
                    missing.append(True)
                else:
                    missing.append(t.isMissing(i))
                    if t.isMissing(i) is False:
                        attributes[i]=t.value(i)
        elif isinstance(t, list):
            l=len(t)
            key=-999
            attributes=[0]*l
            missing=[]
            for i in range(l):
                if math.isinf(t[i]):
                    missing.append(True)
                else:
                    missing.append(False)
                    attributes[i]=t[i]


