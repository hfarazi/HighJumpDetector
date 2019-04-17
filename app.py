from PyQt5.QtCore import Qt, QThread, QTimer
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QVBoxLayout, QApplication, QSlider

from Camera import Camera
from MyImageWidget import MyImageWidget


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
