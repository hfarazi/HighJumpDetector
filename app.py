from PyQt5.QtCore import Qt, QThread, QTimer
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QVBoxLayout, QApplication, QSlider
from PyQt5.QtGui import QImage, QPainter
import numpy as np
import cv2


class MyImageWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.image = QImage()
        self._red = (0, 0, 255)
        self._width = 2
        self._min_size = (30, 30)

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


class Camera:
    def __init__(self, cam_num):
        self.cam_num = cam_num
        self.cap = None
        self.last_frame = np.zeros((1, 1))

    def initialize(self):
        self.cap = cv2.VideoCapture(self.cam_num)

    def get_frame(self):
        ret, self.last_frame = self.cap.read()
        return self.last_frame

    def acquire_movie(self, num_frames):
        movie = []
        for _ in range(num_frames):
            movie.append(self.get_frame())
        return movie

    def set_brightness(self, value):
        self.cap.set(cv2.CAP_PROP_BRIGHTNESS, value)

    def get_brightness(self):
        return self.cap.get(cv2.CAP_PROP_BRIGHTNESS)

    def close_camera(self):
        self.cap.release()

    def __str__(self):
        return 'OpenCV Camera {}'.format(self.cam_num)


class StartWindow(QMainWindow):
    def __init__(self, cam=None):
        super().__init__()
        self.camera = cam

        self.central_widget = QWidget()
        self.button_frame = QPushButton('Acquire Frame', self.central_widget)
        self.button_movie = QPushButton('Start Movie', self.central_widget)
        self.image_view = MyImageWidget()
        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 10)

        self.layout = QVBoxLayout(self.central_widget)
        self.layout.addWidget(self.button_frame)
        self.layout.addWidget(self.button_movie)
        self.layout.addWidget(self.image_view)
        self.layout.addWidget(self.slider)
        self.setCentralWidget(self.central_widget)

        self.button_frame.clicked.connect(self.update_image)
        self.button_movie.clicked.connect(self.start_movie)
        self.slider.valueChanged.connect(self.update_brightness)

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_movie)

        self.movie_thread = None

    def update_image(self):
        frame = self.camera.get_frame()
        if len(frame) > 1:
            self.image_view.image_data_slot(frame)

    def update_movie(self):
        if len(self.camera.last_frame) > 1:
            self.image_view.image_data_slot(self.camera.last_frame)

    def update_brightness(self, value):
        value /= 10
        self.camera.set_brightness(value)

    def start_movie(self):
        self.movie_thread = MovieThread(self.camera)
        self.movie_thread.start()
        self.update_timer.start(30)


class MovieThread(QThread):
    def __init__(self, cam):
        super().__init__()
        self.camera = cam

    def run(self):
        self.camera.acquire_movie(2000)


camNumber = 0
camera = Camera(camNumber)
camera.initialize()

app = QApplication([])
start_window = StartWindow(camera)
start_window.show()
app.exit(app.exec_())
