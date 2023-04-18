import asyncio

from PyQt5.QtCore import QObject, pyqtSignal, QVariant

from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice

import qasync

class QBleakClient(QObject):
    dataReceived = pyqtSignal(bytearray)
    connected = pyqtSignal()
    disconnected = pyqtSignal()

    def __init__(self, deviceName="", txUUID="", rxUUID=""):
        super().__init__()
        self.deviceName = deviceName
        self.txUUID = txUUID
        self.rxUUID = rxUUID

    @qasync.asyncSlot()
    async def connect(self):
        print("Scanning devices...")
        devices = await BleakScanner.discover()
        
        for device in devices:
            print(f'Device name: {device.name}')
            if device.name == self.deviceName:
                self.client = BleakClient(
                    device, 
                    disconnected_callback=self._handle_disconnect
                )
                await self.start()
                self.connected.emit()
                return
        print("Device not found.")
        self.disconnected.emit()
            
    async def start(self):
        try:
            await self.client.connect()
            await self.client.start_notify(self.txUUID, self._handle_read)
        except:
            self.disconnected.emit()

    async def stop(self):
        try:
            await self.client.disconnect()
        except:
            self.disconnected.emit()

    async def write(self, data):
        try:
            await self.client.write_gatt_char(self.rxUUID, data)
        except:
            self.disconnected.emit()

    def _handle_disconnect(self) -> None:
        self.disconnected.emit()

    def _handle_read(self, _: int, data: bytearray) -> None:
        self.dataReceived.emit(data)
        