import cv2
import os
import datetime
import time
import logging

import state
from util.service import Service
import controllers.program as program_controller
import controllers.image as image_controller

logger = logging.getLogger(__name__)


class Camera(Service):


    def __init__(self):
        super().__init__()
        self.set_interval(30E9)
        self.camera = None


    def run_loop(self):
        self.setup_camera()

        if not state.get_global_setting('devmode') and not self.is_daytime():
            return

        try:
            self.capture_image()
        except:
            logger.exception('Failed to capture image')
            self.shutdown_camera()


    def run_end(self):
        self.shutdown_camera()


    def setup_camera(self):
        if self.camera is None:
            self.camera = cv2.VideoCapture(0)
            time.sleep(5)

            if not self.camera.isOpened():
                logger.error('Camera could not be opened')
                self.camera = None
                return

            resolution = state.get_service_setting('camera', 'resolution')
            self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
            self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])


    def shutdown_camera(self):
        if self.camera:
            self.camera.release()
        self.camera = None


    def is_daytime(self):
        current_time = datetime.datetime.now().time()
        later = current_time >= state.get_global_setting('sunrise')
        early = current_time <= state.get_global_setting('sunset')
        return later and early


    def capture_image(self):
        if self.camera:
            ret, frame = self.camera.read()
            if ret is True and frame is not None:
                file_name = f'{int(time.time() * 1e3)}.png'
                file_path = os.path.join(state.get_global_setting('image_dir'), file_name)
                logger.info(f'Saving {file_path} image')
                cv2.imwrite(file_path, frame)
                program_controller.increment_info_key('total_bytes_taken', os.stat(file_path).st_size) 
                image_controller.set_latest_image(frame)
