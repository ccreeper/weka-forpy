import cgitb
import sys
import arff
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from Instances import *
from Preprocess import PreprocessPanel


#弃用

class MainWindow(QMainWindow):

    def __init__(self,parent=None):
        super().__init__(parent)
        self.preprocessPanel=PreprocessPanel(self)
        self.initSetting()


    def initSetting(self):
        #窗口中置
        screen=QDesktopWidget().screenGeometry()
        size=self.geometry()
        self.move((screen.width()-size.width())/2,(screen.height()-size.height())/2)

        #窗口禁止拉伸
        self.setFixedSize(self.width(),self.height())

    def mousePressEvent(self, a0:QMouseEvent):
        if a0.button()==Qt.LeftButton:
            self.setFocus()

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