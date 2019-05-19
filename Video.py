import cv2
import numpy as np


class VideoPlayer:
    def __init__(self, path):
        self.curFrame = 0
        self.cap = cv2.VideoCapture(path)
        self.path = path
        self.last_frame = np.zeros((1, 1))
        self.totalFrames = self.cap.get(cv2.CAP_PROP_FRAME_COUNT)
        self.fps = 240#self.cap.get(cv2.CAP_PROP_FPS)

    def get_frame(self):
        ret, self.last_frame = self.cap.read()
        self.curFrame += 1
        return self.last_frame

    def set_cur_frame(self, number):
        if 0 <= number < self.totalFrames:
            self.curFrame = number
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.curFrame-2)
            self.get_frame()

    def close_camera(self):
        self.cap.release()

    def __str__(self):
        return 'OpenCV Video {}'.format(self.path)
