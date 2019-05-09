from core.Stats import Stats

from core.Utils import Utils


class AttributeStats():
    def __init__(self):
        self.intCount=0
        self.realCount=0
        self.missingCount=0
        self.distinctCount=0
        self.uniqueCount=0
        self.totalCount=0
        self.nominalCounts=None #type:list[int]
        self.nominalWeights=None #type:list[float]
        self.numericStats=None  #type:Stats

    def addDistinct(self,value:float,count:int,weight:float):
        if count>0:
            if count == 1:
                self.uniqueCount+=1

            if value == int(value):
                self.intCount+=count
            else:
                self.realCount+=count

            if self.nominalCounts is not None:
                self.nominalCounts[int(value)]=count
                self.nominalWeights[int(value)]=weight
            if self.numericStats is not None:
                self.numericStats.add(value,weight)
                self.numericStats.calculateDerived()
        self.distinctCount+=1

    def toString(self):
        string= Utils.padLeft("Type", 4) + Utils.padLeft("Nom", 5) + \
                Utils.padLeft("Int", 5) + Utils.padLeft("Real", 5) + \
                Utils.padLeft("Missing", 12) + \
                Utils.padLeft("Unique", 12) + \
                Utils.padLeft("Dist", 6)

        if self.nominalCounts is not None:
            string=string+' '
            for i in range(len(self.nominalCounts)):
                string= string + Utils.padLeft("C[" + i + "]", 5)
        string=string+'\n'

        percent = round(100.0 * self.intCount / self.totalCount)
        if self.nominalCounts is not None:
            string= string + Utils.padLeft("Nom", 4) + ' '
            string= string + Utils.padLeft(str(percent), 3) + "% "
            string= string + Utils.padLeft(str(0), 3) + "% "
        else:
            string= string + Utils.padLeft("Num", 4) + ' '
            string= string + Utils.padLeft(str(0), 3) + "% "
            string= string + Utils.padLeft(str(percent), 3) + "% "
        percent = round(100.0 * self.realCount / self.totalCount)
        string= string + Utils.padLeft(str(percent), 3) + "% "
        string= string + Utils.padLeft(str(self.missingCount), 5) + " /"
        percent =round(100.0 * self.missingCount / self.totalCount)
        string= string + Utils.padLeft(str(percent), 3) + "% "
        string= string + Utils.padLeft(str(self.uniqueCount), 5) + " /"
        percent =round(100.0 * self.uniqueCount / self.totalCount)
        string= string + Utils.padLeft(str(percent), 3) + "% "
        string= string + Utils.padLeft(str(self.distinctCount), 5) + ' '
        if self.nominalCounts is not None:
            for i in range(len(self.nominalCounts)):
                string= string + Utils.padLeft(str(self.nominalCounts[i]), 5)
        string=string+'\n'
        return string
