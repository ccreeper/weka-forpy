import copy
from configparser import ConfigParser
from typing import *

from gui.designUI.Editor import Ui_Form
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from core.Capabilities import Capabilities
from core.PluginManager import PluginManager
from core.Utils import Utils
from gui.GOETreeNode import GOETreeNode
from gui.HierarchyPropertyParser import HierarchyPropertyParser
from gui.TreeWidget import TreeWidget
from gui.common.GenericObjectEditorHistory import GenericObjectEditorHistory


class GenericObjectEditor(QObject):
    classifier_changed = pyqtSignal(str)

    def __init__(self, canChangeClassInDialog: bool = False, parent=None):
        super().__init__(parent)
        self.m_canChangeClassInDialog = canChangeClassInDialog
        self.m_History = GenericObjectEditorHistory()
        self.m_Object = None  # type:object
        self.m_Backup = None
        self.m_EditorComponent = None  # type:GOEPansel
        self.m_ObjectNames = None  # type:Dict[str,HierarchyPropertyParser]
        self.m_CancelWasPressed = False
        self.m_treeNodeOfCurrentObject = None  # type:GOETreeNode
        self.m_ClassType=None       #type:type
        self.m_CapabilitiesFilter=None  #type:Capabilities
        self.loadProperties()

    def setClassType(self, tp: type):
        self.m_ClassType = tp
        self.m_ObjectNames = self.getClassesFromProperties()

    def loadProperties(self):
        try:
            cf = ConfigParser()
            cf.read("./core/config/GenericObject.conf")
            kvs = cf.items("Classifier")
            for item in kvs:
                PluginManager.addPlugin("Classifier", item[1])
            kvs = cf.items("Clusterer")
            for item in kvs:
                PluginManager.addPlugin("Clusterer",item[1])
            kvs = cf.items("Filter")
            for item in kvs:
                PluginManager.addPlugin("Filter", item[1])
        except BaseException as e:
            print(repr(e))

    def getCapabilitiesFilter(self):
        return self.m_CapabilitiesFilter

    def getClassesFromProperties(self) -> Dict[str, HierarchyPropertyParser]:
        hpps = dict()
        className = self.m_ClassType.__name__
        cls = PluginManager.getPluginNamesOfType(className)
        if cls is None:
            return hpps
        b = ""
        for s in cls:
            b += s + ","
        listS = b[0:-1]
        typeOptions = self.sortClassesByRoot(listS)
        Utils.debugOut("All Class:", typeOptions)
        if typeOptions is not None:
            enm = typeOptions.keys()
            for root in enm:
                typeOption = typeOptions.get(root)
                hpp = HierarchyPropertyParser()
                hpp.build(typeOption, ',')
                hpps.update({root: hpp})
        return hpps

    def setCapabilitiesFilter(self,value:Capabilities):
        self.m_CapabilitiesFilter=Capabilities(None)
        self.m_CapabilitiesFilter.assign(value)


    def sortClassesByRoot(self, classes: str) -> Dict[str, str]:
        if classes is None:
            return None
        roots = dict()
        li = []
        hpp = HierarchyPropertyParser()
        separator = hpp.getSeperator()
        clsList = classes.split(',')
        for clsname in clsList:
            root = self.getRootFromClass(clsname, separator)
            if root is None:
                continue
            if root not in roots:
                li = []
                roots.update({root: li})
            else:
                li = roots.get(root)
            li.append(clsname)
        result = dict()
        enm = roots.keys()
        for root in enm:
            li = roots.get(root)
            tmpStr = ""
            for i in range(len(li)):
                if i > 0:
                    tmpStr += ","
                tmpStr += li[i]
            result.update({root: tmpStr})
        return result

    def getRootFromClass(self, clsname: str, separator: str):
        try:
            index = clsname.index(separator)
            return clsname[0:index]
        except ValueError:
            return None

    def setValue(self, o: object):
        if self.m_ClassType is None:
            return
        if not isinstance(o, self.m_ClassType):
            return
        self.setObject(o)
        self.updateObjectNames()
        self.m_CancelWasPressed = False
        self.classifier_changed.emit(o.__class__.__name__)

    def updateObjectNames(self):
        if self.m_ObjectNames is None:
            self.m_ObjectNames = self.getClassesFromProperties()
        if self.m_Object is not None:
            className = self.m_Object.__module__
            root = self.getRootFromClass(className, HierarchyPropertyParser().getSeperator())
            hpp = self.m_ObjectNames.get(root)
            if hpp is not None:
                if not hpp.contains(className):
                    hpp.add(className)

    def setObject(self, c: object):
        if self.getValue() is not None:
            trueChange = (c != self.getValue())
        else:
            trueChange = True
        self.m_Backup = copy.deepcopy(self.m_Object)
        self.m_Object = c
        if self.m_EditorComponent is not None:
            self.m_EditorComponent.updateChildPropertySheet()
        if trueChange:
            pass
            # TODO 改变通知

    def getValue(self):
        return copy.deepcopy(self.m_Object)

    def getCustomEditor(self) -> 'GOEPanel':
        if self.m_EditorComponent is None:
            self.m_EditorComponent = GOEPanel(self)
        return self.m_EditorComponent

    # getChooseClassPopupMenu
    def getTreeMenu(self) -> QTreeWidget:
        self.updateObjectNames()
        self.m_treeNodeOfCurrentObject = None
        tree = self.createTree(self.m_ObjectNames)
        if self.m_treeNodeOfCurrentObject is not None:
            tree.setCurrentItem(self.m_treeNodeOfCurrentObject)
        else:
            root = tree.topLevelItem(0)
            if root != -1:
                tree.setCurrentItem(root)
        tree.itemClicked.connect(self.treeValueChanged)
        return tree

    def treeValueChanged(self, item: GOETreeNode, column: int):
        if item is None:
            return
        if item.isLeaf():
            self.classSelected(item.getClassnameFromPath())

    def classSelected(self, className: str):
        if self.m_Object is not None and self.m_Object.__module__ == className:
            self.classifier_changed.emit(self.m_Object.__class__.__name__)
            return
        clsType = Utils.loadClassForName(className)
        self.setValue(clsType())
        if self.m_EditorComponent is not None:
            self.m_EditorComponent.updateChildPropertySheet()

    def createTree(self, hpps: Dict[str, HierarchyPropertyParser]) -> QTreeWidget:
        if len(hpps) > 1:
            superRoot = GOETreeNode("root")
        else:
            superRoot = None
        root = None
        for hpp in hpps.values():
            hpp.goToRoot()
            root = GOETreeNode(hpp.getValue())
            self.addChildrenToTree(root, hpp)
            if superRoot is None:
                superRoot = root
            else:
                superRoot.addChild(root)
        tree = TreeWidget()
        tree.addTopLevelItem(root)
        return tree

    def addChildrenToTree(self, tree: 'GOETreeNode', hpp: HierarchyPropertyParser):
        for i in range(hpp.numChildren()):
            hpp.goToChild(i)
            child = GOETreeNode(hpp.getValue())
            if self.m_Object is not None and self.m_Object.__module__ == hpp.fullValue():
                self.m_treeNodeOfCurrentObject = child
            tree.addChild(child)
            self.addChildrenToTree(child, hpp)
            hpp.goToParent()

    def getHistory(self):
        return self.m_History



class GOEPanel(QWidget, Ui_Form):
    update_object_signal=pyqtSignal()
    def __init__(self, editor: GenericObjectEditor, parent=None):
        super().__init__(parent)
        super().setupUi(self)
        self.m_Editor = editor
        self.m_ClassNameLabel = self.classNameLabel
        self.m_okBut = self.okBtn
        self.m_cancelBut = self.cancelBtn
        # self.m_ChildPropertySheet=self.propertyWidget
        self.m_Editor.m_Backup = copy.deepcopy(editor.m_Object)
        self.m_ChildPropertySheet = self.propertyWidget
        self.m_ChildPropertySheet.setEnabled(True)
        self.update_object_signal.connect(self.m_ChildPropertySheet.updateObject)
        # TODO 监听改变
        self.m_okBut.clicked.connect(self.okButtonClick)
        self.m_cancelBut.clicked.connect(self.cancelButtonClick)

        if editor.m_ClassType is not None:
            editor.m_ObjectNames = editor.getClassesFromProperties()
            if editor.m_Object is not None:
                editor.updateObjectNames()
                self.updateChildPropertySheet()

    def okButtonClick(self):
        self.update_object_signal.emit()
        self.m_Editor.m_CancelWasPressed = False
        self.m_Editor.m_Backup = copy.deepcopy(self.m_Editor.m_Object)
        self.close()

    def cancelButtonClick(self):
        self.m_Editor.m_CancelWasPressed = True
        if self.m_Editor.m_Backup is not None:
            self.m_Editor.m_Object = copy.deepcopy(self.m_Editor.m_Backup)
            # m_Support.firePropertyChange("", null, null);
            self.m_Editor.m_ObjectNames = self.m_Editor.getClassesFromProperties()
            self.m_Editor.updateObjectNames()
            self.updateChildPropertySheet()
        self.close()
        # TODO

    def updateChildPropertySheet(self):
        className = "None"
        if self.m_Editor.m_Object is not None:
            className = self.m_Editor.m_Object.__module__
            print("className:", className)
        self.m_ClassNameLabel.setText(className)
        self.m_ChildPropertySheet.setTarget(self.m_Editor.m_Object)
        # self.m_ChildPropertySheet.show()

# Test
# from classifiers.Classifier import Classifier
# from classifiers.rules.ZeroR import ZeroR
# import sys
# if __name__=='__main__':
#     app=QApplication(sys.argv)
#     ce=GenericObjectEditor()
#     ce.setClassType(Classifier)
#     initial=ZeroR()
#     ce.setValue(initial)
#     goe=ce.getCustomEditor()
#     goe.adjustSize()
#     goe.show()
#     sys.exit(app.exec_())
