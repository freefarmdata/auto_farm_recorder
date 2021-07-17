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


def get_esp_input(ip: str):
    return f"""\
    -i http://{ip}:81/stream \
    """


def get_webcam_input():
    return f"""\
    -re \
    -f avfoundation \
    -pix_fmt yuyv422 \
    -framerate 15 \
    -i "0:0" \
    """


def get_tuned_encoding_pipeline(name: str, options: dict):
    """
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

    # -vprofile baseline \
    # 
    # -movflags +faststart \
    # 
    # -fflags nobuffer \
    # 
    # -crf {options.get('crf')} \
    
    


    return f"""\
    -vcodec h264 \
    -vf "drawtext=text='%{{localtime\: {name} --- %m/%d/%Y %I.%M.%S %p}}':fontsize=10:fontcolor=white@0.8:x=10:y=10:shadowcolor=red@0.6:shadowx=1:shadowy=1" \
    -preset veryfast \
    -tune zerolatency \
    -pix_fmt yuv420p \
    -x264opts no-scenecut \
    -sc_threshold 0 \
    -vsync 1 \
    -bufsize {options.get('bufsize')} \
    -minrate {options.get('minrate')} \
    -maxrate {options.get('maxrate')} \
    -force_key_frames "expr:gte(t,n_forced*1)" \
    -keyint_min {options.get('keyint_min')} \
    -g {options.get('g')} \
    -framerate {options.get('framerate')} \
    -r {options.get('framerate')} \
    """


def get_hls_output_pipeline(output_file: str):
    return f"""\
    -f hls \
    -hls_flags delete_segments+independent_segments \
    -hls_segment_type mpegts \
    -hls_allow_cache 0 \
    -hls_list_size 1 \
    -hls_time 1 \
    {output_file} \
    """


def get_mp4_output_pipeline(output_file: str):
    return f"""\
    -vcodec h264 \
    {output_file} \
    """


def launch_stream(ip: str, name: str, output_directory: str):
    """
    params:
        - ip - the ip address of source video
        - name - the designated name of stream
        - output_directory - the folder to save stream

    http://underpop.online.fr/f/ffmpeg/help/hls-2.htm.gz
    https://ffmpeg.org/ffmpeg-formats.html#hls-1
    https://ffmpeg.org/ffmpeg-all.html#hls-2
    https://sites.google.com/site/linuxencoding/x264-ffmpeg-mapping
    https://videoblerg.wordpress.com/2017/11/10/ffmpeg-and-how-to-use-it-wrong/
    https://superuser.com/questions/564402/explanation-of-x264-tune
    https://trac.ffmpeg.org/wiki/Encode/H.264
    https://github.com/video-dev/hls.js/blob/master/docs/API.md
    https://distributedstack.dev/ffmpeg-video-hls-http-live-streaming/
    https://trac.ffmpeg.org/wiki/StreamingGuide
    https://sonnati.wordpress.com/2011/08/30/ffmpeg-%E2%80%93-the-swiss-army-knife-of-internet-streaming-%E2%80%93-part-iv/
    https://trac.ffmpeg.org/wiki/Creating%20multiple%20outputs
    https://hlsbook.net/category/ffmpeg/
    """
    output_hls_file = os.path.join(output_directory, f'{name}.m3u8')
    output_mp4_file = os.path.join(output_directory, f'{name}.mp4')

    live_options = { 'minrate': '512k', 'bufsize': '512k', 'maxrate': '1M', 'crf': 23, 'framerate': 60, 'keyint_min': 120, 'g': 120 }
    #live_options = { 'minrate': '256k', 'bufsize': '512k', 'maxrate': '512k', 'crf': 23, 'framerate': 15, 'keyint_min': 30, 'g': 30 }
    #live_options = { 'minrate': '128k', 'bufsize': '256k', 'maxrate': '256k', 'crf': 23, 'framerate': 10, 'keyint_min': 20, 'g': 20 }

    input = get_esp_input(ip)
    #input = get_webcam_input()
    # input = """\
    # -i rtsp://10.0.9.150/axis-media/media.amp \
    # """
    encoding = get_tuned_encoding_pipeline(name, live_options)
    output_hls = get_hls_output_pipeline(output_hls_file)
    #output_mp4 = get_hls_output_pipeline(output_mp4_file)

    command = f"ffmpeg {input} {encoding} {output_hls}"

    logger.info(f'Running ffmpeg pipeline: {command}')

    return subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def set_stream_settings(ip: str):
    """
    Sets default settings to the AI Tinker ESP32 Camera Module Board
    """
    settings_map = {
        'framesize': 4, # set 1024x768
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
        output_dir = self.config.get('stream_dir')
        clean_up_stream(self.name, output_dir)
        set_stream_settings(self.ip)
        self.process = launch_stream(self.ip, self.name, output_dir)


    def run_loop(self):
        if self.process.poll():
            self.stop()
    

    def run_end(self):
        clean_up_stream(self.name, self.config.get('video_dir'))
