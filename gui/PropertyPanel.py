from GenericObjectEditor import GenericObjectEditor
from typing import *
#TODO
class PropertyPanel():
    def __init__(self,pe:GenericObjectEditor,ignoreCustomPanel:bool=False):
        self.m_HasCustomPanel=False
        self.m_Editor=pe
        if not ignoreCustomPanel :
            self.m_CustomPanel=self.m_Editor.

