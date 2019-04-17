import numpy as np
from PyQt5.QtGui import QImage, QPainter
from PyQt5.QtWidgets import QWidget


class MyImageWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = QImage()
        self._red = (0, 0, 255)
        self._width = 2
        self._min_size = (400, 400)
        self.image_data_slot(np.zeros((480, 480, 3), np.uint8))

    def image_data_slot(self, image_data):
        self.image = self.get_qimage(image_data)
        if self.image.size() != self.size():
            self.setFixedSize(self.image.size())
        self.update()

    @staticmethod
    def get_qimage(image: np.ndarray):
        height, width, colors = image.shape
        bytesPerLine = 3 * width
        image = QImage(image.data, width, height, bytesPerLine, QImage.Format_RGB888)
        image = image.rgbSwapped()
        return image

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawImage(0, 0, self.image)
        self.image = QImage()