# Bluetooth
# PyQt Imports
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QVariant, QThread, QTimer
from qbleakclient import QBleakClient
import json

import qasync

class RasynboardCommunicator(QObject):
    
    #  Signals
    commandRecieved = pyqtSignal(str)
    connected = pyqtSignal()
    disconnected = pyqtSignal()

    # Constructor
    def __init__(self):
        QObject.__init__(self)   
        
        self.svUUID = "deadbeef-0123-4567-89ab-cdef0003daf0"
        self.rxUUID = "deadbeef-0123-4567-89ab-cdef0003daf1"
        
        # Create bluetooth client
        self.client = QBleakClient("DA16600-")

        self.client.connected.connect(self.onConnected)
        self.client.disconnected.connect(self.onDisconnected)
        self.client.dataReceived.connect(self.onConnected)
        self.client.deviceNotFound.connect(self.onDeviceNotFound)
        self.client.scanError.connect(self.onDeviceNotFound)

        # Attempt bluetooth connection when event loop starts
        QTimer.singleShot(0, self.client.connect)

    # Slot to handle data received from bluetooth device
    def onDataReceived(self, _: int, data: bytearray):
        jsonStr = data.decode()
        print(f"Data received: {data}")
        try:
            parsed = json.loads(jsonStr)
        except:
            return
        
        self.commandRecieved.emit(parsed['Action'].lower())

    @qasync.asyncSlot()
    async def onConnected(self):
        await self.client.attachHandle(
            self.client.getCharacteristic(self.svUUID, self.rxUUID),
            self.onDataReceived
        )
        self.connected.emit()
        print('Rasynboard connected!')

    def onDisconnected(self):
        print('Rasynboard disconnected...')
        self.disconnected.emit()
        QTimer.singleShot(4000, self.client.connect)        

    def onDeviceNotFound(self):
        print(f'Rasynboard not found.')
        QTimer.singleShot(4000, self.client.connect)
        
