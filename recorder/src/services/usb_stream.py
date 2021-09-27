import time
import logging
import subprocess
import signal
import os

from fservice import state
from fservice.tservice import TService

import controllers.streams as stream_controller

logger = logging.getLogger()

def launch_stream(config: dict, output_directory: str):
    command = stream_controller.get_pi_usb_encoding_pipeline(config, output_directory)
    if state.get_global_setting('local'):
        command = stream_controller.get_mac_webcam_encoding_pipeline(config, output_directory)

    logger.info(f'Running ffmpeg pipeline: {command}')

    if state.get_global_setting('debug'):
        return subprocess.Popen(command, shell=True)
    
    return subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class USBStream(TService):

    def __init__(self, config):
        super().__init__(name='usb_stream')
        self.set_interval(1E9)
        self.config = config
        self.process = None


    def run_start(self):
        output_dir = state.get_global_setting('stream_dir')
        self.process = launch_stream(self.config, output_dir)


    def run_loop(self):
        if self.process.poll():
            self.stop()
    

    def run_end(self):
        try:
            while True:
                self.process.send_signal(signal.SIGINT)
                if self.process.poll():
                    break
                time.sleep(0.1)
        except:
            pass
