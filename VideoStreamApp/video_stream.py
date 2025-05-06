import os
import sys
import ctypes
import numpy as np
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer

# Load the C++ DLL
mylib = ctypes.CDLL(os.path.join(os.path.dirname(__file__), "OpenCvVideoStream.dll"))


# Define the argument and return types for the C++ functions
mylib.initVideoStream.restype = ctypes.c_int
mylib.getNextFrame.restype = ctypes.c_int
mylib.stopVideoStream.restype = None

class App(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.timer = QTimer()  # Timer to update the frame in the QLabel
        self.timer.timeout.connect(self.update_frame)

        self.stream_started = False  # Flag to check if the stream is running

    def initUI(self):
        self.setWindowTitle('C++ and PyQt Video Stream')
        self.setGeometry(100, 100, 640, 480)

        # Create a label to display the video stream
        self.label = QLabel(self)
        self.label.setFixedSize(640, 480)

        # Create a button to start the video stream
        self.start_button = QPushButton("Start Video Stream", self)
        self.start_button.clicked.connect(self.start_video_stream)

        # Create a button to stop the video stream
        self.stop_button = QPushButton("Stop Video Stream", self)
        self.stop_button.clicked.connect(self.stop_video_stream)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.start_button)
        layout.addWidget(self.stop_button)
        self.setLayout(layout)

    def start_video_stream(self):
        # Initialize the video stream (C++ function)
        result = mylib.initVideoStream()
        if result == 0:
            self.stream_started = True
            self.timer.start(30)  # Start the timer to update frames every 30ms
        else:
            self.label.setText("Failed to start video stream.")

    def update_frame(self):
        if self.stream_started:
            # Create a buffer to hold the image data
            width = 640
            height = 480
            buffer = np.zeros((height, width, 3), dtype=np.uint8)

            # Get the next frame from the C++ backend
            result = mylib.getNextFrame(buffer.ctypes.data_as(ctypes.POINTER(ctypes.c_ubyte)), width, height)

            if result == 0:
                # Convert the buffer to a QImage and display it in the label
                image = QImage(buffer.data, width, height, QImage.Format_RGB888)
                self.label.setPixmap(QPixmap.fromImage(image))
            else:
                self.label.setText("Failed to retrieve frame.")

    def stop_video_stream(self):
        if self.stream_started:
            # Stop the video stream and the timer
            self.timer.stop()
            mylib.stopVideoStream()
            self.stream_started = False
            self.label.setText("Video stream stopped.")
