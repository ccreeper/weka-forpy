from typing import *

from core.Instances import Instances

from classifiers.trees.J48Component.C45Split import C45Split
from classifiers.trees.J48Component.Distribution import Distribution
from classifiers.trees.J48Component.ModelSelection import ModelSelection
from classifiers.trees.J48Component.NoSplit import NoSplit
from core.Utils import Utils


class C45ModelSelection(ModelSelection):
    def selectModel(self,data:Instances,test:Instances=None):
        if test is not None:
            return self.selectModel(data)
        multiVal=True
        averageInfoGain=validModels=0
        checkDistribution=Distribution(data)
        noSplitModel=NoSplit(checkDistribution)
        if Utils.gr(2*self.m_minNoObj, checkDistribution.total()) or \
            Utils.equal(checkDistribution.total(), checkDistribution.perClass(checkDistribution.maxClass())):
            return noSplitModel
        if self.m_allData is not None:
            for attr in data.enumerateAttributes():
                if attr.isNumeric() or Utils.gr(0.3*self.m_allData.numInstances(), attr.numValues()):
                    multiVal=False
                    break
        currentModel=[None]*data.numAttributes()        #type:List[C45Split]
        sumOfWeights=data.sumOfWeight()
        for i in range(data.numAttributes()):
            if i != data.classIndex():
                currentModel[i]=C45Split(i,self.m_minNoObj,sumOfWeights,self.m_useMDLcorrection)
                currentModel[i].buildClassifer(data)
                if currentModel[i].checkModel():
                    if self.m_allData is not None:
                        if data.attribute(i).isNumeric() or \
                            (multiVal or Utils.gr(0.3*self.m_allData.numInstances(), data.attribute(i).numValues())):
                            averageInfoGain=averageInfoGain+currentModel[i].infoGain()
                            validModels+=1
                    else:
                        averageInfoGain=averageInfoGain+currentModel[i].infoGain()
                        validModels+=1
            else:
                currentModel[i]=None
        if validModels == 0:
            return noSplitModel
        averageInfoGain=averageInfoGain/validModels
        minResult=0
        for i in range(data.numAttributes()):
            if i != data.classIndex() and currentModel[i].checkModel():
                if currentModel[i].infoGain() >= averageInfoGain-1e-3 and\
                    Utils.gr(currentModel[i].gainRatio(), minResult):
                    bestModel=currentModel[i]
                    minResult=currentModel[i].gainRatio()
        if Utils.equal(minResult, 0):
            return noSplitModel
        bestModel.distribution().addInstWithUnknown(data,bestModel.attIndex())
        if self.m_allData is not None and not self.m_doNotMakeSplitPointActualValue:
            bestModel.setSplitPoint(self.m_allData)
        return bestModel

