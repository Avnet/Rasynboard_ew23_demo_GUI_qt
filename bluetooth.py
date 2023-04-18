# Bluetooth Imports
from bluepy.btle import Scanner, UUID, Peripheral, DefaultDelegate
from bluepy.btle import BTLEDisconnectError, BTLEGattError

# Python Imports
from PyQt5.QtCore import Qt, QObject, pyqtSignal, QVariant, QThread

import re

# Bluetooth Device Class
class BluetoothDevice(QObject, DefaultDelegate):
    
    # Signals
    error = pyqtSignal(str)
    dataReceived = pyqtSignal(QVariant)
    connected = pyqtSignal()
    disconnected = pyqtSignal()

    # Constructor
    def __init__(self, deviceName, svUUID, rxUUID, txUUID):
        # Become delegate
        DefaultDelegate.__init__(self)
        QObject.__init__(self)

        # Device properties
        self.__deviceName = deviceName
        self.__svUUID = svUUID
        self.__rxUUID = rxUUID
        self.txUUID = txUUID

        # Peripheral
        self.__peripheral = None
        self.__service = None

        self.__connectThread = None

    def connect(self):
        # Scan for devices
        try:
            devices = Scanner().scan(timeout = 1)
        except:
            self.error.emit("Unable to scan for devices.")
            return
        
        # Variable to hold found device
        foundDevice = None

        # Loop through devices to try and find one with matching name
        for dev in devices:
            if re.search(self.__deviceName, str(dev.rawData)):
                foundDevice = dev
                break
        
        if foundDevice == None:
            self.error.emit("Unable to find device with given name.")
            return
        
        # Attempt to connect to found device
        try:
            self.__peripheral = Peripheral(
                foundDevice.addr, 
                foundDevice.addrType,
                foundDevice.iface
            )
        except:
            self.error.emit("Unable to connect to device.")
            return
        else:
            self.__peripheral.withDelegate(self)

            # Attempt to get service
            if not self.__getService():
                return
            
            if not self.__enableNotify():
                return

            self.connected.emit()

    # Function to wait for messages
    def notifierWait(self):
        while True:
            try:
                if self.__peripheral.waitForNotifications(1.0):
                    continue
            except BTLEDisconnectError:
                self.disconnected.emit()
                break
    
    # Attempt to get service
    def __getService(self):
        try:
            self.__service = self.__peripheral.getServiceByUUID(self.__svUUID)
        except:
            self.error.emit("Unable to get service by UUID")
            return None
        
        return True

    # Get handle for given UUID
    def __getHandleForUUID(self, uuid):
        try:
            characteristic = self.__service.getCharacteristics(forUUID=uuid)[0]
        except:
            self.error.emit("Unable to get handle for given UUID")
            return None

        # Return handle
        return characteristic.getHandle()

    # Enable notifications
    def __enableNotify(self):
        # Get Handle for RX service
        handle = self.__getHandleForUUID(self.__rxUUID)
        if None == handle:
            return None
        
        # Get decriptors
        try:
            descriptors = self.__peripheral.getDescriptors(handle, self.__service.hndEnd)
        except:
            self.error.emit("Unable to get descriptors")
            return None
        
        for descriptor in descriptors:
            if descriptor.uuid == 0x2902:
                try:
                    self.__peripheral.writeCharacteristic(descriptor.handle, bytes([1,0]))
                except:
                    self.error.emit("Failed to bind to notifer.")
                    return None
                else:
                    return True
                
        return None
                
    # Delegate function to handle BLE data
    def handleNotification(self, cHandle, data):
        # Emit received data
        self.dataReceived.emit(data)

        # Return with super method return
        return super().handleNotification(cHandle, data)