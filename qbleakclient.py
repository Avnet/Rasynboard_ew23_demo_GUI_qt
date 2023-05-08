import asyncio
from enum import Enum

from PyQt5.QtCore import QObject, pyqtSignal, QVariant

from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice

import qasync

# Enum
class State(Enum):
        Disconnected = 0
        Connecting = 1
        Connected = 2

class QBleakClient(QObject):
    
    # Signals
    dataReceived = pyqtSignal(bytearray)
    connected = pyqtSignal()
    disconnected = pyqtSignal()
    deviceNotFound = pyqtSignal()
    scanError = pyqtSignal()

    def __init__(self, deviceName=""):
        super().__init__()
        self.devices = []
        self.device = None
        self.deviceName = deviceName
        self.state = State.Disconnected
        
    # Slot to start connection process
    @qasync.asyncSlot()
    async def connect(self):

        # Only attempt connection if in disconnected state
        if (self.state != State.Disconnected):
            return
        
        # Update state machine
        self.state = State.Connecting

        # If device not already found search for it
        if not self.device:
            try:
                self.devices = await BleakScanner.discover()
            except:
                self.state = State.Disconnected
                self.scanError.emit()
                return

            # Loop through found devices
            for device in self.devices:
                if self.deviceName in device.name:
                    self.device = device
                    break
            
            # If still not round return
            if not self.device:
                self.state = State.Disconnected
                self.deviceNotFound.emit()
                return
        
        # Create client and attempt to connect
        self.client = BleakClient(
            self.device,
            disconnected_callback = self._handle_disconnect
        )
        await self.start()

    def getCharacteristic(self, serviceUUID, characteristicUUID):
        return self.client.services.get_service(serviceUUID).get_characteristic(characteristicUUID)
    
    async def attachHandle(self, handle, callback):
        await self.client.start_notify(handle, callback)

    # Attempt to establish connection
    async def start(self):
        try:
            await self.client.connect() 
            self.state = State.Connected
            self.connected.emit()
        except BaseException as exception:
            print(f"Connection Error: {exception}")
            self.state = State.Disconnected
            self.disconnected.emit()

    async def stop(self):
        print("Stopping...")
        self.state = State.Disconnected
        try:
            await self.client.disconnect()
        except:
            self.disconnected.emit()        

    async def write(self, uuid, data):
        try:
            await self.client.write_gatt_char(uuid, data)
        except:
            self.disconnected.emit()

    def _handle_disconnect(self, data) -> None:
        self.state = State.Disconnected
        self.disconnected.emit()

    def _handle_read(self, _: int, data: bytearray) -> None:
        self.dataReceived.emit(data)

    async def __del__(self):
        print("I'm deconstructing")
        await self.client.disconnect()
        