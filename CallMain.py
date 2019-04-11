import cgitb
import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Preprocess import PreprocessPanel
from ClustererPanel import ClustererPanel
from ClassifierPanel import ClassifierPanel
from Main import Ui_MainWindow


class MainWindow(QMainWindow,Ui_MainWindow):
    tab_changed_signal=pyqtSignal(QObject)
    def __init__(self,parent=None):
        super().__init__(parent)
        super().setupUi(self)
        self.preprocessPanel=PreprocessPanel(self)
        self.classifierPanel=ClassifierPanel(self)
        self.clusterPanel=ClustererPanel(self)
        self.initSetting()

    def initSetting(self):
        self.setWindowTitle("WkPy")
        #窗口中置
        screen=QDesktopWidget().screenGeometry()
        size=self.geometry()
        self.move((screen.width()-size.width())/2,(screen.height()-size.height())/2)

        #窗口禁止拉伸
        self.setFixedSize(self.width(),self.height())

        self.tabWidget.currentChanged.connect(self.TabClicked)


    def TabClicked(self,index:int):
        if index ==1:
            self.tab_changed_signal.emit(self.classifierPanel)
        elif index == 2:
            self.tab_changed_signal.emit(self.clusterPanel)

    def mousePressEvent(self, a0:QMouseEvent):
        if a0.button()==Qt.LeftButton:
            self.setFocus()

    def getPreprocessPanel(self):
        return self.preprocessPanel

    def getClassiferPanel(self):
        return self.classifierPanel

    def getClustererPanel(self):
        return self.clusterPanel



if __name__ == '__main__':
    cgitb.enable(format='text')
    app = QApplication(sys.argv)
    MainWindow = MainWindow()

    styleFile = './configuration/test.qss'
    with open(styleFile, 'r') as file:
        styleSheet = file.read()
        print(styleSheet)
    MainWindow.setStyleSheet(styleSheet)
    MainWindow.show()

    sys.exit(app.exec_())