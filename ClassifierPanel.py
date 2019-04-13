
# import CallMain
import time
from typing import *

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from copy import *
from Attributes import Attribute
from ClassifierErrorsPlotInstances import ClassifierErrorsPlotInstances
from GenericObjectEditor import GenericObjectEditor,GOEPanel
from Instances import Instances
from OptionHandler import OptionHandler
from PropertyPanel import PropertyPanel
from ResultHistoryPanel import ResultHistoryPanel
from SetInstancesPanel import SetInstancesPanel
from Thread import Thread
from Utils import Utils
from classifiers.Classifier import Classifier
from classifiers.evaluation.Evaluation import Evaluation
from classifiers.rules.ZeroR import ZeroR
from VisualizePanel import VisualizePanel
from MatplotlibWidget import MatplotlibWidget
from PlotData2D import PlotData2D
from Drawable import Drawable

class ClassifierPanel(QObject):
    history_add_visualize_signal=pyqtSignal(str,list,str,PlotData2D)
    def __init__(self,win:'MainWindow'):
        super().__init__()
        self.m_Explorer=win
        self.m_Option=win.option_classifier
        self.m_ChooseBut=win.choose_classifier
        self.m_OutText=win.outText              #type:QTextEdit
        self.m_CVBut=win.cross_radio            #type:QRadioButton
        self.m_TrainBut=win.train_radio         #type:QRadioButton
        self.m_TestSplitBut=win.test_radio      #type:QRadioButton
        self.m_SetTestBut=win.test_set_btn      #type:QPushButton
        self.m_CVText=win.cross_value           #type:QLineEdit
        # self.m_Instances=win.m_Instances        #type:Instances
        self.m_SetTestFrame=None                #type:SetInstancesPanel
        self.m_RunThread=None                      #type:Thread
        self.m_StartBut=win.start_btn           #type:QPushButton
        self.m_StopBut=win.stop_btn             #type:QPushButton
        self.m_ClassCombo=win.classifier_combobox       #type:QComboBox
        # 结果列表
        self.m_History=win.resultList           #type:ResultHistoryPanel
        self.m_ClassifierEditor=GenericObjectEditor()   #type:GenericObjectEditor
        self.m_CEPanel=PropertyPanel(self,self.m_ClassifierEditor)  #type:PropertyPanel
        self.m_CurrentVis=None      #type:VisualizePanel


        self.m_History.outtext_write_signal.connect(self.updateOutputText)
        self.m_selectedEvalMetrics=Evaluation.getAllEvaluationMetricNames() #type:List[str]
        self.m_TestClassIndex=-1
        self.mutex=QMutex()
        self.initalize()

    def updateOutputText(self,text:str):
        self.m_OutText.setText(text)

    def getChooseBut(self):
        return self.m_ChooseBut

    def getOptionBut(self):
        return self.m_Option

    def addToHistoryVisualize(self,name:str, vv:List, visName:str, data:PlotData2D):
        self.m_CurrentVis = VisualizePanel()
        self.m_CurrentVis.setName(visName)
        self.m_CurrentVis.addPlot(data)
        vv.append(self.m_CurrentVis)
        self.m_History.addObject(name, vv)

    def initalize(self):
        self.m_selectedEvalMetrics.remove("Coverage")
        self.m_selectedEvalMetrics.remove("Region size")
        self.m_OutText.setReadOnly(True)
        self.m_OutText.setLineWrapMode(QTextEdit.NoWrap)
        self.m_ClassifierEditor.setClassType(Classifier)
        self.m_ClassifierEditor.setValue(ZeroR())
        self.m_CVBut.setChecked(True)
        self.m_StartBut.setEnabled(False)
        self.m_StopBut.setEnabled(False)
        self.updateRadioLinks()

        self.m_CVBut.clicked.connect(self.updateRadioLinks)
        self.m_TrainBut.clicked.connect(self.updateRadioLinks)
        self.m_TestSplitBut.clicked.connect(self.updateRadioLinks)
        self.m_SetTestBut.clicked.connect(self.setTestSet)
        self.m_StartBut.clicked.connect(self.startClassifier)
        self.m_History.menu_expand_signal.connect(self.createMenu)
        self.history_add_visualize_signal.connect(self.addToHistoryVisualize)


    def setInstances(self,inst:Instances):
        self.m_Instances=inst
        attribNames=[]
        for i in range(inst.numAttributes()):
            tp="("+Attribute.typeToStringShort(inst.attribute(i))+")"
            attribNames.append(tp+inst.attribute(i).name())
        self.m_ClassCombo.clear()
        self.m_ClassCombo.addItems(attribNames)
        if len(attribNames) > 0:
            if inst.classIndex() == -1:
                self.m_ClassCombo.setCurrentIndex(len(attribNames)-1)
            else:
                self.m_ClassCombo.setCurrentIndex(inst.classIndex())
            self.m_ClassCombo.setEnabled(True)
            self.m_StartBut.setEnabled(self.m_RunThread is None)
            self.m_StopBut.setEnabled(self.m_RunThread is not None)
        else:
            self.m_StartBut.setEnabled(False)
            self.m_StopBut.setEnabled(False)

    def setTestSet(self):
        if self.m_SetTestFrame is None:
            self.m_SetTestFrame=SetInstancesPanel(True,True)
            self.m_SetTestFrame.combobox_changed_signal.connect(self.propertyChanged)
        self.m_SetTestFrame.show()

    def propertyChanged(self,classIndex:int):
        self.m_TestClassIndex=classIndex

    def updateRadioLinks(self):
        self.m_SetTestBut.setEnabled(self.m_TestSplitBut.isChecked())
        if self.m_SetTestFrame is not None and not self.m_TestSplitBut.isChecked():
            self.m_SetTestFrame.setVisible(False)
        self.m_CVText.setEnabled(self.m_CVBut.isChecked())

    def startClassifier(self):
        if self.m_RunThread is None:
            self.mutex.lock()
            self.m_StartBut.setEnabled(False)
            self.m_StopBut.setEnabled(True)
            self.mutex.unlock()
            self.m_RunThread=Thread(target=self.threadClassifierRun)
            self.m_RunThread.setPriority(QThread.LowPriority)
            self.m_RunThread.start()

    def threadClassifierRun(self):
        self.m_CEPanel.addToHistory()
        inst=Instances(self.m_Instances)
        trainTimeStart=trainTimeElapsed=testTimeStart=testTimeElapsed=0
        userTestStructure=None
        if self.m_SetTestFrame is not None:
            userTestStructure=deepcopy(self.m_SetTestFrame.getInstances())    #type:Instances
            userTestStructure.setClassIndex(self.m_TestClassIndex)

        #默认outputmodel,output per-class stats,output confusion matrix,store predictions for visualization
        #outputPredictionsText=None
        numFolds=10
        classIndex=self.m_ClassCombo.currentIndex()
        inst.setClassIndex(classIndex)
        classifier=self.m_ClassifierEditor.getValue()           #type:Classifier
        name=time.strftime("%H:%M:%S - ")
        outPutResult=""
        evaluation=None     #type:Evaluation
        grph=None

        if self.m_CVBut.isChecked():
            testMode=1
            numFolds=int(self.m_CVText.text())
            if numFolds<=1:
                raise Exception("Number of folds must be greater than 1")
        elif self.m_TrainBut.isChecked():
            testMode=2
        elif self.m_TestSplitBut.isChecked():
            testMode=3
            # if source is None:
            #     raise Exception("No user test set has been specified")
            if not inst.equalHeaders(userTestStructure):
                QMessageBox.critical(self.m_Explorer, "错误", "测试数据集属性不同")
        else:
            raise Exception("Unknown test mode")
        cname=classifier.__module__
        if cname.startswith("classifiers."):
            name+=cname[len("classifiers."):]
        else:
            name+=cname
        cmd = classifier.__module__
        # if isinstance(classifier,OptionHandler):
        #     cmd+=" "+Utils.joinOptions(classifier.getOptions())
        plotInstances=ClassifierErrorsPlotInstances()
        plotInstances.setInstances(userTestStructure if testMode == 4 else inst)
        plotInstances.setClassifier(classifier)
        plotInstances.setClassIndex(inst.classIndex())
        plotInstances.setPointSizeProportionalToMargin(False)
        outPutResult+="=== Run information ===\n\n"
        outPutResult+="Scheme:       " + cname

        # if isinstance(classifier,OptionHandler):
        #     o=classifier.getOptions()
        #     outPutResult+=" "+Utils.joinOptions(o)
        outPutResult+="\n"
        outPutResult+="Relation:     " + inst.relationName() + '\n'
        outPutResult+="Instances:    " + str(inst.numInstances()) + '\n'
        outPutResult+="Attributes:   " + str(inst.numAttributes()) + '\n'
        if inst.numAttributes()<100:
            for i in range(inst.numAttributes()):
                outPutResult+="              " + inst.attribute(i).name()+ '\n'
        else:
            outPutResult+="              [list of attributes omitted]\n"
        outPutResult+="Test mode:    "
        if testMode == 1:
            outPutResult+=str(numFolds) + "-fold cross-validation\n"
        elif testMode == 2:
            outPutResult+="evaluate on training data\n"
        elif testMode == 3:
            outPutResult+="user supplied test set: "+ str(userTestStructure.numInstances()) + " instances\n"
        outPutResult+="\n"
        self.m_History.addResult(name,outPutResult)
        self.m_History.setSingle(name)

        if testMode == 2  or testMode == 3:
            trainTimeStart=time.time()
            classifier.buildClassifier(inst)
            trainTimeElapsed=time.time()-trainTimeStart
        outPutResult+="=== Classifier model (full training set) ===\n\n"
        outPutResult+=str(classifier)+"\n"
        outPutResult+="\nTime taken to build model: "+ Utils.doubleToString(trainTimeElapsed,2)+ " seconds\n\n"
        self.m_History.updateResult(name,outPutResult)
        if isinstance(classifier,Drawable):
            grph=classifier.graph()

        print("==========update Compelte=================")

        if testMode == 2:
            evaluation=Evaluation(inst)
            evaluation=self.setupEval(evaluation,classifier,inst,plotInstances,False)
            evaluation.setMetricsToDisplay(self.m_selectedEvalMetrics)
            plotInstances.setUp()
            testTimeStart=time.time()
            #TODO
            # if isinstance(classifier,BatchPredictor)
            # else:
            for jj in range(inst.numInstances()):
                plotInstances.process(inst.instance(jj),classifier,evaluation)
            testTimeElapsed=time.time()-testTimeStart
            outPutResult+="=== Evaluation on training set ===\n"
        elif testMode == 1:
            rnd=1
            inst.randomize(rnd)
            if inst.attribute(classIndex).isNominal():
                inst.stratify(numFolds)
            evaluation=Evaluation(inst)
            evaluation=self.setupEval(evaluation,classifier,inst,plotInstances,False)
            evaluation.setMetricsToDisplay(self.m_selectedEvalMetrics)
            plotInstances.setUp()
            for fold in range(numFolds):
                train=inst.trainCV(numFolds,fold,rnd)
                evaluation=self.setupEval(evaluation,classifier,train,plotInstances,True)
                evaluation.setMetricsToDisplay(self.m_selectedEvalMetrics)
                current=deepcopy(classifier)
                current.buildClassifier(train)
                test=inst.testCV(numFolds,fold)
                # TODO
                # if isinstance(classifier,BatchPredictor)
                # else:
                for jj in range(test.numInstances()):
                    plotInstances.process(test.instance(jj),current,evaluation)
            if inst.attribute(classIndex).isNominal():
                outPutResult+="=== Stratified cross-validation ===\n"
            else:
                outPutResult+="=== Cross-validation ===\n"
        elif testMode == 3:
            evaluation=Evaluation(inst)
            evaluation=self.setupEval(evaluation,classifier,inst,plotInstances,False)

            plotInstances.setInstances(userTestStructure)
            evaluation.setMetricsToDisplay(self.m_selectedEvalMetrics)
            plotInstances.setUp()
            # TODO
            # if isinstance(classifier,BatchPredictor)
            testTimeStart=time.time()
            for i in range(userTestStructure.numInstances()):
                instance=userTestStructure.instance(i)
                # if isinstance(classifier,BatchPredictor)
                #else
                plotInstances.process(instance,classifier,evaluation)
            # if isinstance(classifier,BatchPredictor)
            testTimeElapsed=time.time()-testTimeStart
            outPutResult+="=== Evaluation on test set ===\n"
        if testMode != 1:
            mode=""
            if testMode == 2:
                mode="training data"
            elif testMode == 3:
                mode="supplied test set"
            outPutResult+="\nTime taken to test model on " + mode + ": "+ Utils.doubleToString(testTimeElapsed, 2)+ " seconds\n\n"
        outPutResult+=evaluation.toSummaryString(False)+'\n'
        self.m_History.updateResult(name,outPutResult)
        if inst.attribute(classIndex).isNominal():
            outPutResult+=evaluation.toClassDetailsString()+'\n'
            outPutResult+=evaluation.toMatrixString()+'\n'
        self.m_History.updateResult(name,outPutResult)
        Utils.debugOut(outPutResult)

        if(plotInstances is not None and plotInstances.canPlot(False)):
            visName=name+" ("+inst.relationName()+")"
            pl2d=plotInstances.getPlotData(cname)
            plotInstances.cleanUp()
            vv=[]
            trainHeader=Instances(self.m_Instances,0)
            trainHeader.setClassIndex(classIndex)
            vv.append(trainHeader)
            if grph is not None:
                vv.append(grph)
            if evaluation is not None and evaluation.predictions() is not None:
                vv.append(evaluation.predictions())
                vv.append(inst.classAttribute())
            self.history_add_visualize_signal.emit(name,vv,visName,pl2d)


        self.mutex.lock()
        self.m_StartBut.setEnabled(True)
        self.m_StopBut.setEnabled(False)
        self.m_RunThread=None
        self.mutex.unlock()
        print("RunFinished")


    def createMenu(self):
        menu=QMenu()
        showClassifierErrors = menu.addAction(u"Visualize classifier errors")        #type:QAction
        showVisualizeTree = menu.addAction(u"Visualize tree")        #type:QAction

        selectedNames = [i.text() for i in self.m_History.selectedItems()]
        o = None  # type:List
        if selectedNames is not None and len(selectedNames) == 1:
            Utils.debugOut("history_name: ", selectedNames)
            o = self.m_History.getNamedObject(selectedNames[0])
        temp_vp = None  # type:VisualizePanel
        temp_grph = None  # type:str
        if o is not None:
            for i in range(len(o)):
                temp = o[i]
                if isinstance(temp, VisualizePanel):
                    temp_vp = temp
                elif isinstance(temp, str):
                    temp_grph = temp
        if temp_vp is not None:
            showClassifierErrors.setEnabled(True)
            showClassifierErrors.triggered.connect(self.classifierErrorTrigger(temp_vp))
        else:
            showClassifierErrors.setEnabled(False)

        if temp_grph is not None:
            showVisualizeTree.setEnabled(True)
            showVisualizeTree.triggered.connect(self.visualizeTreeTrigger(temp_grph))
        else:
            showVisualizeTree.setEnabled(False)
        menu.exec_(QCursor.pos())


    def classifierErrorTrigger(self,sp:VisualizePanel):
        def visualizeClassifierErrors():
            if sp is not None:
                if sp.getXIndex() == 0 and sp.getYIndex() == 1:
                    sp.setXIndex(sp.getInstances().classIndex())
                    sp.setYIndex(sp.getInstances().classIndex() - 1)
                    plotName = sp.getName()
                    sp.setWindowTitle("Classifier Visualize: " + plotName)
                    sp.draw()
                sp.show()
        return visualizeClassifierErrors

    def visualizeTreeTrigger(self,dotty:str):
        def visualizeTree():
            self.mp=MatplotlibWidget()
            self.mp.setWindowTitle("J48 Decision Tree")
            self.mp.createTree(dotty)
            self.mp.show()
        return visualizeTree

    def setupEval(self,evaluation:Evaluation,classifier:Classifier,inst:Instances,plotInstances:ClassifierErrorsPlotInstances,onlySetPriors:bool):
        # if isinstance(classifier,InputMappedClassifier)...
        #else
        evaluation.setPriors(inst)
        if not onlySetPriors:
            if plotInstances is not None:
                plotInstances.setInstances(inst)
                plotInstances.setClassifier(classifier)
                plotInstances.setClassIndex(inst.classIndex())
                plotInstances.setEvaluation(evaluation)
        return evaluation


