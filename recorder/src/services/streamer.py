import os
import datetime
import time
import sys
import logging

from util.time_util import get_daynight_schedule
from services.esp32_stream import ESP32Stream
from services.usb_stream import USBStream
import controllers.alarms as alarm_controller

from fservice import state
from fservice.tservice import TService

logger = logging.getLogger()


class Streamer(TService):
    """
    Processing the streams from the ESP32 Camera modules
    into clips of a specific length.
    """


    def __init__(self):
        super().__init__(name='streamer')
        self.set_interval(1E9)
        self.streams = []
        self.sunrise, self.sunset = get_daynight_schedule(
            state.get_global_setting('sunrise'),
            state.get_global_setting('sunset')
        )


    def run_start(self):
        alarm_controller.clear_alarm('streamer_service_offline')
        self.initialize_streams()


    def run_loop(self):
        if self.is_daytime() or self.is_online_override():
            alarm_controller.clear_alarm('streamer_service_night')
            self.check_streams()
        elif self.is_offline_override():
            self.stop_streams()
        else:
            alarm_controller.set_info_alarm(
                'streamer_service_night',
                'Streams Offline At Night Time',
                upsert=False
            )
            self.stop_streams()


    def run_end(self):
        self.stop_streams()
        alarm_controller.set_warn_alarm('streamer_service_offline', 'Streamer Service is Offline')


    def is_online_override(self):
        return state.get_service_setting('streamer', 'online_override')

    
    def is_offline_override(self):
        return state.get_service_setting('streamer', 'offline_override')


    def check_streams(self):
        for i in range(len(self.streams)):
            stream = self.streams[i]
            if stream.is_stopped():
                stream_name = stream.config.get('stream_name')
                logger.info(f"Restarting Stream '{stream_name}'")
                alarm_controller.set_info_alarm(
                    f'streamer_stream_{stream_name}_restarted',
                    f'Stream: {stream_name} stopped and restarted',
                )
                new_stream = self.create_stream(stream.config)
                new_stream.start()
                self.streams[i] = new_stream


    def create_stream(self, config) -> TService:
        stream = None
        if config.get('camera_type') == 'esp32':
            stream = ESP32Stream(config)
        elif config.get('camera_type') == 'usb':
            stream = USBStream(config)
        return stream


    def initialize_streams(self):
        configs = state.get_service_setting('streamer', 'streams')
        if configs is not None:
            for config in configs:
                stream = self.create_stream(config)
                stream._stopped = True
                self.streams.append(stream)


    def stop_streams(self):
        for i in range(len(self.streams)):
            self.streams[i].stop_wait()


    def is_daytime(self):
        current_time = datetime.datetime.now().time()
        later = current_time >= self.sunrise
        early = current_time <= self.sunset
        return later and early
