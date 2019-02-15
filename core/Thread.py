
from PyQt5.QtCore import *

class Thread(QThread):
    def __init__(self,target,args=()):
        super().__init__()
        self.target=target
        self.args=args

    def run(self):
        self.target(*self.args)