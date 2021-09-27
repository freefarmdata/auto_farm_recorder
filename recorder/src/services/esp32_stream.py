import os
import sys
import time
import logging
import subprocess

import requests
from fservice import state
from fservice.tservice import TService

import controllers.streams as stream_controller

logger = logging.getLogger()


def launch_stream(config, output_directory: str):
    command = stream_controller.get_esp32_encoding_pipeling(config, output_directory)

    logger.info(f'Running ffmpeg pipeline: {command}')

    if state.get_global_setting('debug'):
        return subprocess.Popen(command, shell=True)
    
    return subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def set_stream_settings(ip: str):
    """
    Sets default settings to the AI Tinker ESP32 Camera Module Board
    """
    settings_map = {
        'framesize': 8, # set 1024x768
        'quality': 30,
        'brightness': 1,
        'ae_level': 1,
        'lenc': 1,
        'raw_gma': 1,
        'wb_mode': 0
    }

    for setting in settings_map:
        value = settings_map[setting]
        url = f'http://{ip}/control?var={setting}&val={value}'
        logger.info(f'Setting {setting} to {value} for camera {ip}')
        status = requests.get(url, timeout=(5, 5)).status_code
        if status != 200:
            raise Exception(f'Failed to set {setting} on esp32: {ip}')


class ESP32Stream(TService):

    def __init__(self, config):
        super().__init__(name='esp32_stream')
        self.set_interval(1E9)
        self.config = config
        self.process = None


    def run_start(self):
        output_dir = state.get_global_setting('stream_dir')
        set_stream_settings(self.config.get('ip_address'))
        self.process = launch_stream(self.config, output_dir)


    def run_loop(self):
        if self.process.poll():
            self.stop()
    

    def run_end(self):
        try:
            while not self.process.poll():
                self.process.kill()
                time.sleep(0.1)
        except:
            pass
