#TODO tomorrow

import importlib
from typing import *
class PluginManager():
    PLUGINS=dict()  #type:dict[str,dict[str,type]]
    @classmethod
    def addPlugin(cls, packageName:str, className:str):
        imp=importlib.import_module(packageName+"."+className)
        cla=getattr(imp,className)
        dt=dict({className:cla})
        cls.PLUGINS.update({packageName:dt})

    @classmethod
    def getPluginNamesOfType(cls,modelName:str)->List[str] :
        if cls.PLUGINS.get(modelName) is not None:
            match=cls.PLUGINS.get(modelName).keys()
            return match
        return None


