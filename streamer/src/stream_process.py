import subprocess
import logging
import time
from threading import Thread

import requests

from config import get_config
from controllers import streams

logger = logging.getLogger()

class StreamProcess(Thread):

    def __init__(self, config: dict):
        super().__init__(name=config.get('stream_name'), daemon=True)
        self.stream_config = config

    def run(self):
        camera_type = self.stream_config.get('camera_type')
        if camera_type == 'usb':
            self.process = self.start_usb_stream()
        elif camera_type == 'esp32':
            self.process = self.start_esp32_stream()
        
        while True:
            if self.process.poll():
                self.process.kill()
                return
            time.sleep(1)
    

    def start_usb_stream(self):
        config = get_config()
        command = streams.get_pi_usb_encoding_pipeline(self.stream_config, config.stream_dir)
        if config.local:
            command = streams.get_mac_webcam_encoding_pipeline(self.stream_config, config.stream_dir)

        logger.info(f'Running ffmpeg pipeline: {command}')

        if config.debug:
            return subprocess.Popen(command, shell=True)
        
        return subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


    def start_esp32_stream(self):
        config = get_config()
        self.set_esp32_stream_settings()

        command = streams.get_esp32_encoding_pipeling(self.stream_config, config.stream_dir)

        if config.debug:
            return subprocess.Popen(command, shell=True)
        
        return subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    
    def set_esp32_stream_settings(self):
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

        ip_address = self.stream_config.get('ip_address')

        for setting in settings_map:
            value = settings_map[setting]
            url = f'http://{ip_address}/control?var={setting}&val={value}'
            logger.info(f'Setting {setting} to {value} for camera {ip_address}')
            if requests.get(url, timeout=(5, 5)).status_code != 200:
                raise Exception(f'Failed to set esp32 settings on {ip_address}')