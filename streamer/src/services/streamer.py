import os
import datetime
import time
import sys
import logging

from util.time_util import get_daynight_schedule
from services.esp32_stream import ESP32Stream
from services.usb_stream import USBStream
import state

sys.path.append('../libs/pystate')

from tservice import TService

logger = logging.getLogger()


class Streamer(TService):
    """
    Processing the streams from the ESP32 Camera modules
    into clips of a specific length.
    """


    def __init__(self):
        super().__init__()
        self.set_interval(1E9)
        self.streams = []
        self.sunrise = None
        self.sunset = None


    def run_start(self):
        self.sunrise, self.sunset = get_daynight_schedule(
            state.get_global_setting('sunrise'),
            state.get_global_setting('sunset')
        )
        self.start_streams()


    def run_loop(self):
        for i in range(len(self.streams)):
            stream = self.streams[i]
            if stream.is_stopped():
                logger.info(f"Restarting Stream '{stream.config.get('name')}'")
                self.streams[i] = self.start_stream(stream.config)

    
    def run_update(self, message):
        if message is not None:
            if message.get('action') == 'attach':
                self.attach_stream(message.get('config'))


    def run_end(self):
        self.stop_streams()

    
    def attach_stream(self, config):
        configs = state.get_service_setting('streamer', 'streams')
        configs.append(config)
        state.set_service_setting('streamer', 'streams', configs)
        self.streams.append(self.start_stream(config))


    def start_stream(self, config) -> TService:
        stream = None
        if config.get('camera_type') == 'esp32':
            stream = ESP32Stream(config)
        elif config.get('camera_type') == 'usb':
            stream = USBStream(config)
        stream.start()
        return stream


    def start_streams(self):
        configs = state.get_service_setting('streamer', 'streams')
        if configs is not None:
            for config in configs:
                self.streams.append(self.start_stream(config))


    def stop_streams(self):
        for i in range(len(self.streams)):
            self.streams[i].stop()
        self.streams = []


    def is_daytime(self):
        current_time = datetime.datetime.now().time()
        later = current_time >= self.sunrise
        early = current_time <= self.sunset
        return later and early
