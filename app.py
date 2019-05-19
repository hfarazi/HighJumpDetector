from PyQt5.QtCore import Qt, QThread, QTimer, QEvent
from PyQt5.QtWidgets import QMainWindow, QWidget, QPushButton, QVBoxLayout, QApplication, QSlider, QLabel, QFileDialog, \
    QMessageBox
from PyQt5.QtGui import QFont
from shutil import copyfile
from Video import VideoPlayer
from MyImageWidget import MyImageWidget
import os
import numpy as np
import time


class MyWidgetSlider(QSlider):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.installEventFilter(self)
        self.setStyleSheet(" background: gray;")
        self.setDisabled(True)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.FocusIn:
            self.setStyleSheet(" background: green;")
            self.valueChanged.emit(self.value())
        elif event.type() == QEvent.FocusOut:
            self.setStyleSheet(" background: gray;")

        return False


class StartWindow(QMainWindow):
    def __init__(self, video=None):
        super().__init__()
        self.video = video
        self.central_widget = QWidget()
        self.button_movie = QPushButton('Open Movie', self.central_widget)
        self.button_save = QPushButton('Save Movie', self.central_widget)
        self.button_save.setDisabled(True)
        self.image_view = MyImageWidget()

        self.sliderStart = MyWidgetSlider(Qt.Horizontal)
        self.sliderEnd = MyWidgetSlider(Qt.Horizontal)
        self.label = QLabel("time=")
        self.label.setFont(QFont("Ubuntu", 20, QFont.Bold))
        self.labelDuration = QLabel("duration=")
        self.labelDuration.setFont(QFont("Ubuntu", 30, QFont.Bold))
        self.labelDuration.setStyleSheet("color: red;")

        self.layout = QVBoxLayout(self.central_widget)
        self.layout.addWidget(self.button_movie)
        self.layout.addWidget(self.button_save)
        self.layout.addWidget(self.image_view)
        self.layout.addWidget(self.sliderStart)
        self.layout.addWidget(self.sliderEnd)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.labelDuration)
        self.setCentralWidget(self.central_widget)

        self.button_movie.clicked.connect(self.start_movie)
        self.button_save.clicked.connect(self.save_movie)
        self.sliderStart.valueChanged.connect(self.update_seekStart)
        self.sliderStart.setFixedHeight(70)
        self.sliderEnd.valueChanged.connect(self.update_seekEnd)
        self.sliderEnd.setFixedHeight(70)

        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_movie)

        self.movie_thread = None

        self.end = self.start = 1
        self.fn = ""

    def update_movie(self):
        if self.video.last_frame is not None and len(self.video.last_frame) > 1:
            self.image_view.image_data_slot(self.video.last_frame)
            self.label.setText(
                "time=" + str(self.video.curFrame * (1000. / self.video.fps)) + "  (" + str(self.video.curFrame) + ")")

    def update_seekStart(self, value):
        self.video.set_cur_frame(value)
        self.start = self.video.curFrame
        self.labelDuration.setText("duration=" + str((self.end - self.start) * (1000. / self.video.fps)) + "  (" + str(
            (self.end - self.start)) + ")")
        self.button_save.setDisabled(self.end <= self.start)

    def update_seekEnd(self, value):
        self.video.set_cur_frame(value)
        self.end = self.video.curFrame
        self.labelDuration.setText("duration=" + str((self.end - self.start) * (1000. / self.video.fps)) + "  (" + str(
            (self.end - self.start)) + ")")
        self.button_save.setDisabled(self.end <= self.start)

    def start_movie(self):
        camPre = "/run/user/1000/gvfs/"
        try:
            camPre += "/" + os.listdir(camPre)[0]
            camPre += "/" + os.listdir(camPre)[0]
            camPre += "/" + os.listdir(camPre)[0]
            camPre += "/" + os.listdir(camPre)[0]
            fn = QFileDialog.getOpenFileName(
                self.central_widget, 'Open profile', camPre,
                filter='mp4 (*.mp4)')[0]
            if fn and os.path.isfile(fn):
                self.fn = fn
                self.video = VideoPlayer(fn)
                self.sliderStart.setRange(0, self.video.totalFrames)
                self.sliderEnd.setRange(0, self.video.totalFrames)
                if "_E_" in fn and "_S_" in fn and "_T_" in fn:
                    self.start=float(fn.split("_S_")[1])-1
                    self.sliderStart.setValue(int(self.start))
                    self.end = float(fn.split("_E_")[1])-1
                    self.sliderEnd.setValue(int(self.end))
                else:
                    self.start=0
                    self.sliderStart.setValue(self.start)
                    self.end = 0
                    self.sliderEnd.setValue(self.end)
                self.sliderStart.setDisabled(False)
                self.sliderEnd.setDisabled(False)
                self.movie_thread = MovieThread(self.video)
                self.movie_thread.start()
                self.update_timer.start(30)
        except Exception as e:
            QMessageBox.about(self, "Error loading file", str(e))

    def save_movie(self):
        camPre = os.path.expanduser("~/HighJumpDetector/")
        try:
            name = QFileDialog.getSaveFileName(self, 'Save File',camPre)
            if len(name[0])>1:
                fn=name[0]
                spfn=fn.split("/")
                fn=fn.replace(".MP4","")
                self.sliderStart.setDisabled(True)
                self.sliderEnd.setDisabled(True)
                self.button_save.setDisabled(True)
                self.video.close_camera()
                self.video.last_frame = np.zeros_like(self.video.last_frame)
                self.image_view.image_data_slot(self.video.last_frame)
                self.movie_thread = None
                fn=fn+"_S_"+str(self.start)+"_S_"+"_E_"+str(self.end)+"_E_"+"_T_"+str((self.end - self.start) * (1000. / self.video.fps))+"_T_"+".mp4"
                copyfile(self.fn,fn)
                os.remove(self.fn)
                self.label.setText("time=")
                self.sliderStart.setValue(0)
                self.sliderEnd.setValue(0)
                QMessageBox.about(self, "Saved!", fn)
        except Exception as e:
            QMessageBox.about(self, "Error loading file", str(e))


class MovieThread(QThread):
    def __init__(self, video):
        super().__init__()
        self.video = video

    def run(self):
        self.video.set_cur_frame(0)


app = QApplication([])
start_window = StartWindow()
start_window.show()
app.exit(app.exec_())
