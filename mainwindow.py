# Qt Imports
from PyQt5.QtCore import QObject
from PyQt5 import QtGui, QtWidgets, uic, QtCore
from PyQt5.QtCore import Qt

from controlwidget import ControlWidget

class MainWindow(QtWidgets.QWidget):

    # Constructor
    def __init__(self):
        super().__init__()
        
         # Get screen dimensions
        app = QtWidgets.QApplication.instance()
        height = app.primaryScreen().size().height()
        width = app.primaryScreen().size().width()
        
        # Create base
        self.__layout = QtWidgets.QVBoxLayout()        
        self.setSizePolicy(
            QtWidgets.QSizePolicy.MinimumExpanding,
            QtWidgets.QSizePolicy.MinimumExpanding
        )

        # Create control
        self.__control = ControlWidget()
        self.__control.setFixedHeight(700)
        self.__control.setFixedWidth(700)

        # Layout
        self.__layout.addWidget(self.__control)
        self.__layout.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        self.setLayout(self.__layout)

        # Resize
        self.resize(width, height)

        self.__active = False

        

    def onSetActive(self, active):
        self.__active = active
        self.__control.setActive(active)

    def onBack(self):
        if self.__active:
            self.__control.triggerLeftState()

    def onNext(self):
        if self.__active:
            self.__control.triggerRightState()

    def onUp(self):
        if self.__active:
            self.__control.triggerUpState()

    def onDown(self):
        if self.__active:
            self.__control.triggerDownState()

    

        
