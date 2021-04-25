import cv2
import os
import datetime
import time
import logging
from multiprocessing import Process

import state
from util.tservice import TService
from util.time_util import profile_func, now_ms, now_ns
import controllers.program as program_controller
import controllers.image as image_controller
from controllers.camera_runner import CameraRunner

logger = logging.getLogger()

def get_daynight_schedule():
    sunrise = state.get_global_setting('sunrise').split(':')
    sunset = state.get_global_setting('sunset').split(':')

    sunrise = datetime.time(*[int(n) for n in sunrise])
    sunset = datetime.time(*[int(n) for n in sunset])

    return sunrise, sunset


class Camera(TService):


    def __init__(self):
        super().__init__()
        self.set_interval(None)
        self.last_save = None
        self.sunrise = None
        self.sunset = None
        self.camera = None


    def run_start(self):
        self.sunrise, self.sunset = get_daynight_schedule()
        resolution = state.get_service_setting('camera', 'resolution')
        interval = state.get_service_setting('camera', 'interval')
        self.camera = CameraRunner(resolution, interval)
        self.camera.start()


    def run_loop(self):
        image = self.camera.poll(timeout=1)
        if image is not None:
            self.save_image(image)

    
    def run_update(self, message):
        if message.get('action') == 'set_interval':
            interval = message.get('interval')
            self.camera.update('set_interval', interval)
            state.set_service_setting('camera', 'interval', interval)


    def run_end(self):
        self.camera.stop()
        self.camera.shutdown(timeout=5)
        self.camera = None


    def is_daytime(self):
        current_time = datetime.datetime.now().time()
        later = current_time >= self.sunrise
        early = current_time <= self.sunset
        return later and early


    def save_image(self, image):
        image_data = image['data']
        image_time = image['time']

        delay = int(now_ms() - image_time)
        file_name = f'{image_time}.png'
        save_frame = int(state.get_service_setting('camera', 'save_frame'))

        if self.last_save is None or now_ns() - self.last_save >= save_frame:
            self.last_save = now_ns()
        
            file_path = os.path.join(state.get_global_setting('image_dir'), file_name)
            logger.info(f'Saving {file_path} image. Delayed: {delay}')
            cv2.imwrite(file_path, image_data)
        
        logger.debug(f'{file_name} delay: {delay}')
        image_controller.set_latest_image(image_data, image_time)
