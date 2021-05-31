import cv2
import os
import datetime
import time
import logging

import state
from util.tservice import TService
from util.time_util import profile_func, now_ms, now_ns
import controllers.alarms as alarm_controller
import controllers.program as program_controller
import controllers.stream as stream_controller

logger = logging.getLogger()

def get_daynight_schedule():
    sunrise = state.get_global_setting('sunrise').split(':')
    sunset = state.get_global_setting('sunset').split(':')

    sunrise = datetime.time(*[int(n) for n in sunrise])
    sunset = datetime.time(*[int(n) for n in sunset])

    return sunrise, sunset


class Stream(TService):
    """
    Processing the streams from the ESP32 Camera modules
    into clips of a specific length.
    """


    def __init__(self):
        super().__init__()
        self.set_interval(None)
        self.sunrise = None
        self.sunset = None
        self.streams = []


    def run_start(self):
        self.sunrise, self.sunset = get_daynight_schedule()
        self.streams = state.get_service_setting('stream', 'stream_ips')


    def run_loop(self):
        pass

    
    def run_update(self, message):
        pass


    def run_end(self):
        pass


    def start_camera(self):
        pass

    
    def stop_camera(self):
        pass


    def is_daytime(self):
        current_time = datetime.datetime.now().time()
        later = current_time >= self.sunrise
        early = current_time <= self.sunset
        return later and early
