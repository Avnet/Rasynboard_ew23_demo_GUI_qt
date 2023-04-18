# Bluetooth
from bluetooth import BluetoothDevice

# PyQt Imports
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QVariant, QThread, QTimer
import json

class RasynboardCommunicator(QObject):
    
    #  Signals
    commandRecieved = pyqtSignal(str)
    connected = pyqtSignal()
    disconnected = pyqtSignal()

    # Constructor
    def __init__(self):
        QObject.__init__(self)   
        
        self.connect() 
    
    def connect(self):
        # Create bluetooth device handler
        self.__device = BluetoothDevice(
            deviceName="DA16600-",
            svUUID="deadbeef-0123-4567-89ab-cdef0003daf0",
            rxUUID="deadbeef-0123-4567-89ab-cdef0003daf1",
            txUUID="deadbeef-0123-4567-89ab-cdef0003daf2"
        )

        # Create thread
        self.__connectThread = QThread()
        self.__device.moveToThread(self.__connectThread)
        
        # Connect slots
        self.__device.connected.connect(self.__onConnected)
        self.__device.disconnected.connect(self.__onDisconnected)
        self.__device.dataReceived.connect(self.__onDataReceived)
        self.__device.error.connect(self.__onError)
        self.__device.connected.connect(self.__device.notifierWait)
        self.__connectThread.started.connect(self.__device.connect)
        self.__connectThread.finished.connect(self.__connectThread.deleteLater)
        self.__connectThread.finished.connect(self.connect)

        # Start thread
        self.__connectThread.start() 

    # Slot to handle data received from bluetooth device
    def __onDataReceived(self, data):
        jsonStr = data.decode()

        try:
            parsed = json.loads(jsonStr)
        except:
            return
        
        self.commandRecieved.emit(parsed['Action'].lower())

    def __onConnected(self):
        self.connected.emit()
        print('Rasynboard connected!')

    def __onDisconnected(self):
        self.disconnected.emit()
        QTimer.singleShot(2000, self.__connectThread.quit)        

    def __onError(self, error):
        print(f'Error: {error}')
        QTimer.singleShot(2000, self.__connectThread.quit)
        
