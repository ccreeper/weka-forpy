
import importlib
from typing import *

class PluginManager():
    PLUGINS=dict()  #type:dict[str,dict[str,type]]
    @classmethod
    def addPlugin(cls, interfaceName:str, className:str):
        imp=importlib.import_module(className)
        clsName=className.split(".")[-1]
        cla=getattr(imp,clsName)
        dt=cls.PLUGINS.get(interfaceName)
        if dt is None:
            dt=dict()
        dt.update({className:cla})
        cls.PLUGINS.update({interfaceName:dt})

    @classmethod
    def getPluginNamesOfType(cls,modelName:str)->List[str] :
        if cls.PLUGINS.get(modelName) is not None:
            match=cls.PLUGINS.get(modelName).keys()
            return match
        return None


