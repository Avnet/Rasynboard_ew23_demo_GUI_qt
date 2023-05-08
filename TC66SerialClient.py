import asyncio

from PyQt5.QtCore import QObject, pyqtSignal, QTimer, QVariant

import qasync

from tc import *

class TC66SerialClient(QObject):
    dataReceived = pyqtSignal(QVariant)
    connectReattemptTimeoutMS = 2000
    requestTimeIntervalMS = 1000

    def __init__(self):
        super().__init__()
        
        # Timer to periodically request data from client
        self.requestTimer = None

        # Single shot timer to connect once event loop starts
        QTimer.singleShot(0, self.connect)

    # Attempt to connect to TC66
    @qasync.asyncSlot()
    async def connect(self):
        # If using serial port, attempt connection
       
        self.client = TcSerialInterface("/dev/ttyACM0", 3)
        try:
            self.client.connect()
        except Exception as e:
            print(f"Unable to connect to serial port: {e}")
            QTimer.singleShot(self.connectReattemptTimeoutMS, self.connect)
            return
        
        # Create timer to request data at specified interval on successful connection
        self.requestTimer = QTimer()
        self.requestTimer.setInterval(self.requestTimeIntervalMS)
        self.requestTimer.timeout.connect(self.requestData)
        self.requestTimer.start()

    # Request data from TC66 client   
    def requestData(self):
        data = None

        # Request data
        try:
            data = self.client.read()
            
        # If problem, stop request timer and attempt to reconnect    
        except Exception as e:
                print(f"Error reading data: {e}")
                self.requestTimer.stop()
                QTimer.singleShot(self.connectReattemptTimeoutMS, self.connect)
                

        # Emit data received
        if data:
            self.dataReceived.emit(data)
       