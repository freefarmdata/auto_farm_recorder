import os
import datetime
import time
import logging

from stream import Stream
from util.tservice import TService
from util.time_util import profile_func, now_ms, now_ns

logger = logging.getLogger()

def get_daynight_schedule(config):
    sunrise = config.get('sunrise').split(':')
    sunset = config.get('sunset').split(':')

    sunrise = datetime.time(*[int(n) for n in sunrise])
    sunset = datetime.time(*[int(n) for n in sunset])

    return sunrise, sunset


class Streamer(TService):
    """
    Processing the streams from the ESP32 Camera modules
    into clips of a specific length.
    """


    def __init__(self, config):
        super().__init__()
        self.set_interval(1E9)
        self.config = config
        self.sunrise = None
        self.sunset = None
        self.streams = []


    def run_start(self):
        self.sunrise, self.sunset = get_daynight_schedule(self.config)
        self.start_streams()


    def run_loop(self):
        pass

    
    def run_update(self, message):
        pass


    def run_end(self):
        self.stop_streams()

    
    def start_streams(self):
        for stream_config in self.config.get('streams'):
            stream = Stream(stream_config.get('ip'), stream_config.get('name'), self.config)
            stream.start()
            self.streams.append(stream)


    def stop_streams(self):
        for stream in self.streams:
            stream.stop()
        self.streams = []


    def is_daytime(self):
        current_time = datetime.datetime.now().time()
        later = current_time >= self.sunrise
        early = current_time <= self.sunset
        return later and early
