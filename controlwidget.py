from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPen
import math
class ControlWidget(QtWidgets.QWidget):
    
    # Init
    def __init__(self):
        super(ControlWidget, self).__init__()

        # Control properties
        self.__innerGapWidth = 10
        self.__innerRadiusFactor = 1
        self.__arcLineWidth = 140

        # Colors
        self.__backgroundColor = QtGui.QColor('#03465C')
        self.__controlColor = QtCore.Qt.gray
        self.__selectedColor = QtGui.QColor("#009600")
        self.__textColor = QtCore.Qt.white
        self.__activeColor = QtGui.QColor("#EB7B0C")

        # States
        self.__controlText = "\"OK SYNTIANT\""

        self.__upStateActive = False
        self.__downStateActive = False
        self.__leftStateActive = False
        self.__rightStateActive = False
        self.__controlStateActive = False

    def setActive(self, active):
        # Set flag
        self.__controlStateActive = active

        # Force redraw
        self.update()

    def triggerUpState(self):
        # Set flag
        self.__upStateActive = True

        # Create timer to clear state
        QTimer.singleShot(1000, self.__clearUpState)

        # Force redraw
        self.update()

    def __clearUpState(self):
        # Set flag
        self.__upStateActive = False

        # Force redraw
        self.update()

    def triggerDownState(self):
        # Set flag
        self.__downStateActive = True

        # Create timer to clear state
        QTimer.singleShot(1000, self.__clearDownState)

        # Force redraw
        self.update()

    def __clearDownState(self):
        # Set flag
        self.__downStateActive = False

        # Force redraw
        self.update()

    def triggerLeftState(self):
        # Set flag
        self.__leftStateActive = True

        # Create timer to clear state
        QTimer.singleShot(1000, self.__clearLeftState)

        # Force redraw
        self.update()

    def __clearLeftState(self):
        # Set flag
        self.__leftStateActive = False

        # Force redraw
        self.update()

    def triggerRightState(self):
        # Set flag
        self.__rightStateActive = True

        # Create timer to clear state
        QTimer.singleShot(1000, self.__clearRightState)

        # Force redraw
        self.update()

    def __clearRightState(self):
        # Set flag
        self.__rightStateActive = False

        # Force redraw
        self.update()

    # Draw Functions

    # Paint
    def paintEvent(self, e):
        # Create painter
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        # Draw main background
        self.drawMainBackground(painter)
        
        # Draw controls
        self.drawUpButton(painter)
        self.drawRightButton(painter)
        self.drawDownButton(painter)
        self.drawLeftButton(painter)

        # Draw cutouts
        self.drawCutouts(painter)

        # Draw center circle
        self.drawControlCenter(painter)

        # Draw Control Text
        self.drawControlText(painter)

        # Commit changes
        painter.end()

    # Draws main background
    def drawMainBackground(self, painter):
        # Create brush
        brush = QtGui.QBrush()
        brush.setColor(self.__backgroundColor)
        brush.setStyle(Qt.SolidPattern)

        painter.setBrush(brush)
        painter.drawEllipse(0,0, self.width(), self.width())

    # Draw arc for control
    def drawControlArc(self, painter, start, color):
        # Define arc radius and stroke attributes
        arcRadius = self.width() * self.__innerRadiusFactor - self.__innerGapWidth
        painter.setPen(QPen(color, self.__arcLineWidth, cap=Qt.FlatCap))
        
        # Paint the arc
        painter.drawArc(
            (self.__arcLineWidth + self.__innerGapWidth * 2) / 2,
            (self.__arcLineWidth + self.__innerGapWidth  * 2) / 2,
            self.width() - self.__arcLineWidth - (self.__innerGapWidth * 2),
            self.width() - self.__arcLineWidth - (self.__innerGapWidth * 2),
            start * 16, 
            90 * 16
        )

    # Draw control
    def drawControlCenter(self, painter):
        # Create Brush
        brush = QtGui.QBrush()
        brush.setStyle(Qt.SolidPattern)

        if self.__upStateActive or self.__downStateActive or self.__leftStateActive or self.__rightStateActive:
            brush.setColor(self.__selectedColor)
        elif self.__controlStateActive:
            brush.setColor(self.__activeColor)
        else:
            brush.setColor(self.__backgroundColor)
        
        painter.setBrush(brush)
        
        arcRadius = (self.width() - self.width() * self.__innerRadiusFactor) + self.__arcLineWidth + self.__innerGapWidth
        size = self.width() + arcRadius
        
        offset = (self.width() - arcRadius ) / 4
        painter.drawEllipse(offset, offset, size/2, size/2)

    # Draw Text
    def drawText(self, painter, x, y, height, width, color, size, text):
        # Set Color
        painter.setPen(color)
        
        # Update font
        font = painter.font()
        font.setPointSize(size)
        painter.setFont(font)

        # Draw Text
        painter.drawText(
            x, 
            y, 
            width, 
            height,
            Qt.AlignHCenter | Qt.AlignVCenter,
            text
        )

        # painter.setPen(Qt.red)
        # painter.drawRect(
        #     x, 
        #     y, 
        #     width, 
        #     height
        # )


    # Draw cutouts
    def drawCutouts(self, painter):
        # Line color
        painter.setPen(QPen(
            self.__backgroundColor,
            self.__innerGapWidth,
            cap=Qt.FlatCap
        ))

        midPoint = self.width()/2
        radius = self.width()/2

        upperLeftX = midPoint + radius * math.cos(math.radians(45))
        upperLeftY = midPoint + radius * math.sin(math.radians(45))
        
        botRightX = midPoint + radius * math.cos(math.radians(45+180))
        botRightY = midPoint + radius * math.sin(math.radians(45+180))


        rightRightX = midPoint + radius * math.cos(math.radians(-45))
        upperRightY = midPoint + radius * math.sin(math.radians(-45))
        
        botLeftX = midPoint + radius * math.cos(math.radians(-45+180))
        botLeftY = midPoint + radius * math.sin(math.radians(-45+180))

        painter.drawLine(upperLeftX, upperLeftY, botRightX, botRightY)
        painter.drawLine(rightRightX, upperRightY, botLeftX, botLeftY)

    # Draw up control
    def drawUpButton(self, painter):
        self.drawControlArc(
            painter, 
            45, 
            self.__selectedColor if self.__upStateActive else self.__controlColor
        )
        
        x = 0
        y = self.__innerGapWidth
        width = self.width()
        height = self.__arcLineWidth
        self.drawText(
            painter,
            x,
            y,
            height,
            width,
            self.__textColor,
            28,
            "UP"
        )

    # Draw left control
    def drawLeftButton(self, painter):
        self.drawControlArc(
            painter, 
            45+90, 
            self.__selectedColor if self.__leftStateActive else self.__controlColor
        )

        # Draw Arrow
        x = 0
        y = 0
        width = self.__arcLineWidth
        height = self.width()
        self.drawText(
            painter,
            x,
            y,
            height,
            width,
            self.__textColor,
            28,
            "BACK"
        )

    # Draw down control
    def drawDownButton(self, painter):
        self.drawControlArc(
            painter, 
            45+180, 
            self.__selectedColor if self.__downStateActive else self.__controlColor
        )

        x = 0
        y = self.width() - self.__arcLineWidth
        width = self.width()
        height = self.__arcLineWidth
        self.drawText(
            painter,
            x,
            y,
            height,
            width,
            self.__textColor,
            28,
            "DOWN"
        )

    # Draw right control
    def drawRightButton(self, painter):
        self.drawControlArc(
            painter, 
            45+270, 
            self.__selectedColor if self.__rightStateActive else self.__controlColor
        )

        # Draw Arrow
        x = self.width() - self.__arcLineWidth
        y = 0
        width = self.__arcLineWidth
        height = self.width()
        self.drawText(
            painter,
            x,
            y,
            height,
            width,
            self.__textColor,
            28,
            "NEXT"
        )
    
    def drawControlText(self, painter):
        # Set Color
        painter.setPen(self.__textColor)
        
        # Update font
        font = painter.font()
        font.setPointSize(28)

        painter.setFont(font)

        if self.__upStateActive:
            self.__controlText = "\"UP\""
        elif self.__downStateActive:
            self.__controlText = "\"DOWN\""
        elif self.__leftStateActive:
            self.__controlText = "\"BACK\""
        elif self.__rightStateActive:
            self.__controlText = "\"NEXT\""
        else:
            self.__controlText = "\"OK SYNTIANT\""

        # Draw Text
        painter.drawText(
            0, 
            0, 
            self.width(), 
            self.width(),
            Qt.AlignHCenter | Qt.AlignVCenter,
            self.__controlText
        )