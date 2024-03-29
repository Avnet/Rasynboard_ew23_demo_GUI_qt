#!/bin/python3
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QEvent, QTimer
from mainwindow import MainWindow
from powerwindow import PowerWindow
from communicator import RasynboardCommunicator
from TC66BLEClient import TC66BLEClient
from TC66SerialClient import TC66SerialClient
from qbleakclient import QBleakClient

import asyncio
import sys
import argparse
import signal
import functools
import qasync
import config

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
        
        # Request timer
        self.requestTimer = None

        # Data buffer
        self.dataBuffer = bytearray()
        self.bufferIdx = 0

        if config.pwrSource == 'serial':
            self.tc66Client = TC66SerialClient()
        elif config.pwrSource == 'ble':
            self.tc66Client = TC66BLEClient()
        else:
            self.tc66Client = TC66SerialClient()

        self.tc66Client.dataReceived.connect(self.onTC66DataReceived)

    @qasync.asyncSlot()
    async def onBleCon(self):
        print("con")
        svUUID="deadbeef-0123-4567-89ab-cdef0003daf0"
        rxUUID="deadbeef-0123-4567-89ab-cdef0003daf1"
        
        print(f"characteristic: {self.client.getCharacteristic(svUUID, rxUUID)}")
        #await self.client.write(bytes([1,0]))

    def onBleDis(self):
        print("dis")
        QTimer.singleShot(2000, self.client.connect)

    def onBleData(self, data):
        print(f"data: {data}")

    def onRasynboardConnected(self):
        self.mainWindow.show()
        self.powerWindow.hide()
        
    def onRasynboardDisconnected(self):
        self.powerWindow.show()
        self.mainWindow.hide()
        
    def onTC66DataReceived(self, data):
        self.powerWindow.updateCurrent(round(data["current"] * 1000.0, 2))

    def onBLEData(self, data):
        print(f'Data: {data}')

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
                self.active
                self.activeTimer.setInterval(5000)
                self.mainWindow.onSetActive(True)
            elif event.key() == Qt.Key_Backspace:
                self.powerWindow.show()
                self.mainWindow.hide()
            elif event.key() == Qt.Key_Escape:
                self.exit()

        # Return
        return ret     

app:Application = None
loop = None
# Application entry point
def main():
    global app

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--pwrSrc", help="Define source for TC66 power measurement <serial | BLE")
    parser.add_argument("-n", "--bleName", help="Define the BLE advertisement name")
    parser.add_argument("-c", "--comPort", type=str, help="Define the microUSB TC66C Com Port")

    args = parser.parse_args()

    # Set defaults if arguments are not set
    if (args.pwrSrc):
        config.pwrSource = args.pwrSrc
    else:
        config.pwrSource = "serial"
        
    if (args.bleName):
        config.rasynBoardName = args.bleName
    else:
        config.rasynBoardName = "DA16600-"
    if (args.comPort):
        config.comPort = args.comPort
    else:
        config.comPort = "com5"

    print('TC66C Data Source is ', config.pwrSource)
    print('BLE Name is ', config.rasynBoardName)
    print('TC66C com port = ', config.comPort)

    # Create application
    app = Application(sys.argv)
    loop = qasync.QEventLoop(app)
    #loop.add_signal_handler(signal.SIGHUP, functools.partial(shutdown, loop))
    #loop.add_signal_handler(signal.SIGTERM, functools.partial(shutdown, loop))

    # Start event loop
    with loop:
        loop.run_forever()
    print("All done....")
    asyncio.run(app.communicator.client.stop())
    asyncio.run(app.tc66Client.client.stop())

def shutdown(loop):
    asyncio.get_running_loop().run_until_complete(app.communicator.client.stop())
    asyncio.get_running_loop().run_until_complete(app.tc66Client.client.stop())
    for task in asyncio.Task.all_tasks():
        task.cancel()

# Fix Ctrl-C
signal.signal(signal.SIGINT, signal.SIG_DFL)

# Bind main entrypoint
if __name__ == "__main__":
    main()