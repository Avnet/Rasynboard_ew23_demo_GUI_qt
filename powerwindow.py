# Qt Imports
from PyQt5.QtCore import QObject
from PyQt5 import QtGui, QtWidgets, uic, QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QPixmap

class PowerWindow(QtWidgets.QWidget):

    # Constructor
    def __init__(self):
        super().__init__()
        uic.loadUi("form.ui", self)
        self.image.setPixmap(QPixmap("avnet-info.png"))
        self.show()
    
    def updateCurrent(self, value):
        self.currentMeasurement.setText(f'{value} mA')