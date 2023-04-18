#!/bin/python3

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QEvent, QTimer
from mainwindow import MainWindow
from powerwindow import PowerWindow
from communicator import RasynboardCommunicator
from TC66BLEClient import TC66BLEClient

import sys
import signal

import qasync

# Application
class Application(QApplication):
    
    # Application constructor
    def __init__(self, args):
        # Call super constructor
        super(Application, self).__init__(args)
        self.powerWindow = PowerWindow()
        self.powerWindow.updateCurrent("--")

        # Create main window
        self.mainWindow = MainWindow()
        
        # Create communicator
        self.communicator = RasynboardCommunicator()
        self.communicator.commandRecieved.connect(self.onCommandReceived)
        self.communicator.connected.connect(self.onRasynboardConnected)
        self.communicator.disconnected.connect(self.onRasynboardDisconnected)

        self.active = False
        self.activeTimer = QTimer()
        self.activeTimer.timeout.connect(self.timeout)

        self.tc66Client = TC66BLEClient()
        self.tc66Client.dataReceived.connect(self.onTC66DataReceived)

    def onRasynboardConnected(self):
        self.mainWindow.show()
        self.powerWindow.hide()
        
    def onRasynboardDisconnected(self):
        self.powerWindow.show()
        self.mainWindow.hide()
        
    def onTC66DataReceived(self, data):
        self.powerWindow.updateCurrent(round(data["current"] * 1000.0, 2))

    # Slot for handling data from Rasynboard
    def onCommandReceived(self, command):
        self.mainWindow.show()
        self.powerWindow.hide()

        if command == "up":
            self.mainWindow.onUp()
        elif command == "down":
            self.mainWindow.onDown()
        elif command == "next":
            self.mainWindow.onNext()
        elif command == "back":
            self.mainWindow.onBack()
        elif command == "wakeup":
            self.active = True
            self.mainWindow.onSetActive(True)
        elif command == "idle":
            self.powerWindow.show()
            self.mainWindow.hide()
            

        if self.active:
            self.activeTimer.setInterval(5000)
            self.activeTimer.start()

    def timeout(self):
        self.activeTimer.stop()
        self.active = False
        self.mainWindow.onSetActive(False)

    # Key press to simulate system
    def notify(self, receiver, event):
        # Call super
        ret = QApplication.notify(self, receiver, event)
        
        # Respond to keypress event
        if event.type() == QEvent.KeyPress:
            if event.key() == Qt.Key_Up:
                self.mainWindow.onUp()
            elif event.key() == Qt.Key_Down:
                self.mainWindow.onDown()
            elif event.key() == Qt.Key_Right:
                self.mainWindow.onNext()
            elif event.key() == Qt.Key_Left:
                self.mainWindow.onBack()
            elif event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
                self.mainWindow.onSetActive(True)
            elif event.key() == Qt.Key_Escape:
                exit(0)

        # Return
        return ret     

# Application entry point
def main():
    # Create application
    app = Application(sys.argv)
    loop = qasync.QEventLoop(app)
    # Start event loop
    with loop:
        loop.run_forever()


# Fix Ctrl-C
signal.signal(signal.SIGINT, signal.SIG_DFL)

# Bind main entrypoint
if __name__ == "__main__":
    main()