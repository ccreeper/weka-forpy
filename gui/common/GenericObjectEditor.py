from PluginManager import PluginManager
from TreeNodeButton import TreeNodeButton,HierarchyPropertyParser
from typing import *
import copy

class GenericObjectEditorHistory():
    def __init__(self):
        self.m_History=[]

class GenericObjectEditor():
    def __init__(self,canChangeClassInDialog:bool=False):
        self.m_canChangeClassInDialog=canChangeClassInDialog
        self.m_History=GenericObjectEditorHistory()
        self.m_Object=None              #type:object
        self.m_Backup=None
        self.m_EditorComponent=None     #type:GOEPanel
        self.m_ObjectNames=None         #type:Dict[str,HierarchyPropertyParser]
        self.m_CancelWasPressed=False

    #TODO 直接对每个类生成代替
    def setClassType(self,tp:type):
        self.m_ClassType=tp
        self.m_ObjectNames=self.getClassesFromProperties()

    def getClassesFromProperties(self)->Dict[str,HierarchyPropertyParser]:
        hpps=dict()
        className=self.m_ClassType.__name__
        cls=PluginManager.getPluginNamesOfType(className)
        if cls is None:
            return hpps
        b=""
        for s in cls:
            b+=s+","
        listS=b[0:-1]
        typeOptions=self.sortClassesByRoot(listS)
        if typeOptions is not None:
            enm = typeOptions.keys()
            for root in enm:
                typeOption=typeOptions.get(root)
                hpp=HierarchyPropertyParser()
                hpp.build(typeOption,',')
                hpps.update({root:hpp})
        return hpps

    def sortClassesByRoot(self,classes:str)->Dict[str,str]:
        if classes is None:
            return None
        roots=dict()
        li=[]
        hpp=HierarchyPropertyParser()
        separator=hpp.getSeperator()
        clsList=classes.split(',')
        for clsname in clsList:
            root=self.getRootFromClass(clsname,separator)
            if root is None:
                continue
            if root not in roots:
                li=[]
                roots.update({root:li})
            else:
                li=roots.get(root)
            li.append(clsname)
        result=dict()
        enm=roots.keys()
        for root in enm:
            li=roots.get(root)
            tmpStr=""
            for i in range(len(li)):
                if i>0:
                    tmpStr += ","
                tmpStr += li[i]
            result.update({root:tmpStr})
        return result



    def getRootFromClass(self,clsname:str,separator:str):
        try:
            index=clsname.index(separator)
            return clsname[0:index]
        except ValueError:
            return None


    def setValue(self,o:object):
        if self.m_ClassType is None:
            return
        if not isinstance(o,self.m_ClassType):
            return
        self.setObject(o)
        self.updateObjectNames()
        self.m_CancelWasPressed=False

    def updateObjectNames(self):
        if self.m_ObjectNames is None:
            self.m_ObjectNames=self.getClassesFromProperties()
        if self.m_Object is not None:
            className=self.m_Object.__class__.__name__
            root=self.getRootFromClass(className,HierarchyPropertyParser().getSeperator())
            hpp=self.m_ObjectNames.get(root)
            if hpp is not None:
                if not hpp.contains(className):
                    hpp.add(className)


    #TODO
    def setObject(self,c:object):
        if self.getValue() is not None:
            trueChange= (c != self.getValue())
        else:
            trueChange=True
        self.m_Backup=self.m_Object
        self.m_Object=c
        if self.m_EditorComponent is not None:
            self.m_EditorComponent.updateChildPropertySheet()
        if trueChange:
            pass
            #TODO 改变通知


    def getValue(self):
        return copy.deepcopy(self.m_Object)




from Editor import Ui_Form
from PropertySheetPanel import PropertySheetPanel
from PyQt5.QtWidgets import *

class GOEPanel(QWidget,Ui_Form):
    def __init__(self,editor:GenericObjectEditor,parent=None):
        super().__init__(parent)
        super().setupUi(self)
        self.m_ClassNameLabel=self.classNameLabel
        self.m_okBut=self.okBtn
        # self.m_ChildPropertySheet=self.propertyWidget
        self.m_Editor=editor

        self.m_ChildPropertySheet=PropertySheetPanel()
        #TODO 监听改变


        #TODO
    def updateChildPropertySheet(self):
        className="None"
        if self.m_Editor.m_Object is not None:
            className = self.m_Editor.m_Object.__class__.__name__
        self.m_ClassNameLabel.setText(className)
        self.m_ChildPropertySheet.setTarget(self.m_Editor.m_Object)
        #TODO 可能需要重新调整大小

