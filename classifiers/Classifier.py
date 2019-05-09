from core.Instances import Instances,Instance


class Classifier():
    @classmethod
    def getAllProperties(cls):pass
    @classmethod
    def getAllMethods(cls):pass
    def buildClassifier(self, data: Instances):pass
    def getCapabilities(self):pass
    def distributionForInstance(self,instance:Instance):pass
