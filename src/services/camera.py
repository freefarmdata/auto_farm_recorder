import cv2
import os
import datetime
import time
import logging
from service import Service

logger = logging.getLogger(__name__)

import api

def now_ms():
    return int(time.time() * 1e3)


class Camera(Service):
    def __init__(self):
        super().__init__()
        self.camera = None
        self.resolution = (1920, 1080)
        self.sunrise = datetime.time(6, 0, 0, 0)
        self.sunset = datetime.time(23, 0, 0, 0)
        self.data_dir = '/etc/recorder'
        self.image_dir = os.path.join(self.data_dir, 'images')

    def run_start(self):
        self.set_interval(5E9)
        self.setup_data_dirs()

    def setup_data_dirs(self):
        if not os.path.isdir(self.data_dir):
            os.mkdir(self.data_dir)

        if not os.path.isdir(self.image_dir):
            os.mkdir(self.image_dir)

    def setup_camera(self):
        if self.camera is None:
            self.camera = cv2.VideoCapture(0)
            time.sleep(5)

            if not self.camera.isOpened():
                logger.error('Camera could not be opened')
                self.camera = None
                return

            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, self.resolution[0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, self.resolution[1])

    def shutdown_camera(self):
        if self.camera:
            self.camera.release()
        self.camera = None
        self.video = None

    def run_loop(self):
        self.setup_camera()

        if not self.is_daytime():
            return

        try:
            self.capture_image()
        except Exception as e:
            logger.error(e)
            self.shutdown_camera()

    def is_daytime(self):
        current_time = datetime.datetime.now().time()
        return current_time >= self.sunrise and current_time <= self.sunset

    def capture_image(self):
        if self.camera and self.video:
            ret, frame = self.camera.read()
            if ret is True and frame is not None:
                file_name = f'{now_ms()}.png'
                file_path = os.path.join(self.image_dir, file_name)
                cv2.imwrite(file_path, frame)
                api.set_latest_image(frame)
