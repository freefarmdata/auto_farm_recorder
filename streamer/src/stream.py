import os
import time
import logging
import subprocess

import requests

from util.tservice import TService

logger = logging.getLogger()

def clean_up_stream(name: str, output: str):
    """
    Removes all references to the HLS playlist for the
    given stream name
    """
    files = filter(lambda f: f.startswith(name), os.listdir(output))
    for file_name in files:
        os.remove(os.path.join(output, file_name))


def launch_stream(ip: str, name: str, output: str):
    """
    http://underpop.online.fr/f/ffmpeg/help/hls-2.htm.gz
    https://ffmpeg.org/ffmpeg-formats.html#hls-1
    https://ffmpeg.org/ffmpeg-all.html#hls-2
    https://sites.google.com/site/linuxencoding/x264-ffmpeg-mapping
    https://videoblerg.wordpress.com/2017/11/10/ffmpeg-and-how-to-use-it-wrong/

    params:
        - ip - the ip address of source video
        - name - the designated name of stream
        - output - the folder to save stream

    ffmpeg params:
        - c:v - video type
        - minrate - minimum bitrate
        - bufsize - standard bitrate
        - maxrate - maximum bitrate
        - crf - quality ranging from 0-51
        - preset - ultrafast - veryslow, default settings for optimization
        - r - output FPS
        - g - keyframes
    """
    output_file = os.path.join(output, f'{name}.m3u8')

    # text overlay of month/day/year hour.minute.second
    draw_text_overlay = f"drawtext=text='%{{localtime\: {name} --- %m/%d/%Y %I.%M.%S %p}}':fontcolor=white@0.8:x=10:y=10"

   

    command = f"""
    ffmpeg \
        -i http://{ip}:81/stream \
            -c:v libx264 \
            -vf "{draw_text_overlay}" \
            -sc_threshold 0 \
            -tune film \
            -pix_fmt yuv420p \
            -preset veryfast \
            -vsync 1 \
            -threads 0 \
            -minrate 256k \
            -bufsize 256k \
            -maxrate 2048k \
            -x264opts no-scenecut \
            -crf 23 \
            -r 30 \
            -g 120 \
        -f hls \
            -hls_flags delete_segments+independent_segments \
            -hls_segment_type mpegts \
            -hls_allow_cache 0 \
            -hls_list_size 1 \
            -hls_time 1 \
            {output_file}
    """

    logger.info(f'Running ffmpeg pipeline: {command}')

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
        assert requests.get(url, timeout=(5, 5)).status_code == 200

class Stream(TService):

    def __init__(self, ip, name, config):
        super().__init__()
        self.set_interval(1E9)
        self.ip = ip
        self.name = name
        self.config = config
        self.process = None


    def run_start(self):
        output_dir = self.config.get('video_dir')
        clean_up_stream(self.name, output_dir)
        set_stream_settings(self.ip)
        self.process = launch_stream(self.ip, self.name, output_dir)


    def run_loop(self):
        if self.process.poll():
            self.stop()
    

    def run_end(self):
        clean_up_stream(self.name, self.config.get('video_dir'))
