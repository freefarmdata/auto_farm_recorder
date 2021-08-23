import os
import time
import sys
import logging
import subprocess

from fservice import state
from fservice.tservice import TService

import controllers.streams as stream_controller

logger = logging.getLogger()

def get_video_input():
    return f"""\
    -f v4l2 \
    -codec:v h264 \
    -i /dev/video0 \
    """


def launch_stream(config: dict, output_directory: str):
    output_hls_file = os.path.join(output_directory, f'{config.get("stream_name")}.m3u8')

    input = get_video_input()
    if state.get_global_setting('local'):
        input = stream_controller.get_mac_webcam_input()

    encoding = stream_controller.get_encoding_pipeline(config)
    output_hls = stream_controller.get_hls_output_pipeline(config, output_hls_file)

    command = f"ffmpeg {input} {encoding} {output_hls}"

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
        stream_controller.clean_up_stream(self.config.get('stream_name'), output_dir)
        self.process = launch_stream(self.config, output_dir)


    def run_loop(self):
        if self.process.poll():
            self.stop()
    

    def run_end(self):
        stream_controller.clean_up_stream(
            self.config.get('stream_name'),
            state.get_global_setting('stream_dir')
        )
