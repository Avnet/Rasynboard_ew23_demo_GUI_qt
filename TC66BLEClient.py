import asyncio

from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QVariant

from bleak import BleakScanner, BleakClient
from bleak.backends.device import BLEDevice
from qbleakclient import QBleakClient
import qasync
from time import time
from Crypto.Cipher import AES

KEY = [
	88, 33, -6, 86, 1, -78, -16, 38,
	-121, -1, 18, 4, 98, 42, 79, -80,
	-122, -12, 2, 96, -127, 111, -102, 11,
	-89, -15, 6, 97, -102, -72, 114, -120
]

class TC66BLEClient(QObject):
    dataReceived = pyqtSignal(QVariant)

    def __init__(self):
        super().__init__()
        
        # Create bluetooth client
        self.client = QBleakClient("BT24-M")
        self.rxUUID = "0000ffe1-0000-1000-8000-00805f9b34fb"
        
        self.client.connected.connect(self.connected)
        self.client.disconnected.connect(self.disconnected)
        self.client.deviceNotFound.connect(self.onDeviceNotFound)
        self.client.dataReceived.connect(self.onDataReceived)
        self.client.scanError.connect(self.onDeviceNotFound)

        # Request timer
        self.requestTimer = None

        # Data buffer
        self.dataBuffer = bytearray()
        self.bufferIdx = 0

        # Single shot timer to connect once event loop starts
        QTimer.singleShot(0, self.client.connect)

    def onDataReceived(self, _, data):
        self.dataReceived.emit(self.decode(data))

    def append(self, data):
        try:
            self.dataBuffer.extend(data)
            self.bufferIdx += len(data)
        except BufferError:
            pass

    def decode_integer(self, data, first_byte, divider=1):
        temp4 = data[first_byte] & 255
        temp3 = data[first_byte + 1] & 255
        temp2 = data[first_byte + 2] & 255
        temp1 = data[first_byte + 3] & 255
        return ((((temp1 << 24) | (temp2 << 16)) | (temp3 << 8)) | temp4) / float(divider)

    def decrypt(self):
        key = []

        for index, value in enumerate(KEY):
            key.append(value & 255)

        aes = AES.new(bytes(key), AES.MODE_ECB)
        try:
            return aes.decrypt(self.dataBuffer)
        except ValueError:
            print("Decrypt error.")
        
    def decode(self, data=None):
        if data is not None:
            self.append(data)

        data = self.decrypt()

        if self.decode_integer(data, 88) == 1:
            temperature_multiplier = -1
        else:
            temperature_multiplier = 1

        return {
            "timestamp": time(),
            "voltage": self.decode_integer(data, 48, 10000),
            "current": self.decode_integer(data, 52, 100000),
            "power": self.decode_integer(data, 56, 10000),
            "resistance": self.decode_integer(data, 68, 10),
            "accumulated_current": self.decode_integer(data, 72),
            "accumulated_power": self.decode_integer(data, 76),
            "accumulated_time": None,
            "temperature": self.decode_integer(data, 92) * temperature_multiplier,
            "data_plus": self.decode_integer(data, 96, 100),
            "data_minus": self.decode_integer(data, 100, 100),
            "mode_id": None,
            "mode_name": None
        }

    # Request measurements
    @qasync.asyncSlot()
    async def requestMeasurements(self):
        self.dataBuffer = bytearray()
        self.bufferIdx = 0
        await self.client.write(self.rxUUID, "bgetva\r\n".encode())
    
    # Slot called when device connected
    @qasync.asyncSlot()
    async def connected(self):
        await self.client.attachHandle(self.rxUUID, self.onDataReceived)
        self.requestTimer = QTimer()
        self.requestTimer.setInterval(1000)
        self.requestTimer.timeout.connect(self.requestMeasurements)
        self.requestTimer.start()

    # Attempt to reconnect after disconnection
    def disconnected(self):
        if self.requestTimer:
            self.requestTimer.stop()
        QTimer.singleShot(5000, self.client.connect)
        print("TC66 Disconnected.")
    
    def onDeviceNotFound(self):
        QTimer.singleShot(5000, self.client.connect)
        print("TC66 Not Found.")