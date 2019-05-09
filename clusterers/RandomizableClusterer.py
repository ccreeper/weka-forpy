from clusterers.AbstractClusterer import AbstractClusterer


class RandomizableClusterer(AbstractClusterer):
    propertyList = AbstractClusterer.propertyList[:]
    methodList = AbstractClusterer.methodList[:]
    propertyList.append('seed')
    def __init__(self):
        super().__init__()
        self.Seed=1
        self.seed=self.Seed

    def setSeed(self,value:int):
        self.seed=value

    def getSeed(self):
        return self.seed
