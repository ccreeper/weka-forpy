from typing import *
from classifiers.trees.J48.ClassifierTree import ClassifierTree
from classifiers.trees.J48.ModelSelection import ModelSelection
from Instances import Instances,Instance

class PruneableClassifierTree(ClassifierTree):
    def __init__(self,toSelectLocModel:ModelSelection,pruneTree:bool,num:int,cleanup:bool,seed:int):
        super().__init__(toSelectLocModel)
        self.pruneTheTree = pruneTree
        self.numSets = num
        self.m_cleanup = cleanup
        self.m_seed = seed

    #TODO