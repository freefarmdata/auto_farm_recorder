import os
import time
import logging
import subprocess

from util.tservice import TService
import state

logger = logging.getLogger()


def clean_up_stream(name: str, output: str):
    """
    Removes all references to the HLS playlist for the
    given stream name
    """
    files = filter(lambda f: f.startswith(name), os.listdir(output))
    for file_name in files:
        os.remove(os.path.join(output, file_name))


def get_video_input():
    return f"""\
    -f v4l2 \
    -codec:v h264 \
    -i /dev/video0 \
    """


def get_tuned_encoding_pipeline(options: dict):
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
    # -fflags nobuffer \
    # -sc_threshold 0 \
    # -crf {options.get('crf')} \
    # -vf "drawtext=text='%{{localtime\: default --- %m/%d/%Y %I.%M.%S %p}}':fontsize=100:fontcolor=yellow@0.8:x=10:y=10:shadowcolor=blue@0.6:shadowx=2:shadowy=2" \

    return f"""\
    -vcodec copy \
    -preset veryfast \
    -tune zerolatency \
    -pix_fmt yuv420p \
    -movflags +faststart \
    -x264opts no-scenecut \
    -vsync {options.get('vsync')} \
    -video_size {options.get('video_size')} \
    -bufsize {options.get('bufsize')} \
    -minrate {options.get('minrate')} \
    -maxrate {options.get('maxrate')} \
    -framerate {options.get('framerate')} \
    -force_key_frames "expr:gte(t,n_forced*1)" \
    -keyint_min {options.get('keyint_min')} \
    -g {options.get('g')} \
    """


def get_hls_output_pipeline(options: dict, output_file: str):
    return f"""\
    -f hls \
    -hls_flags delete_segments \
    -hls_segment_type mpegts \
    -hls_allow_cache 0 \
    -hls_list_size {options.get('hls_list_size')} \
    -hls_time {options.get('hls_time')} \
    {output_file} \
    """


def get_mp4_output_pipeline(output_file: str):
    return f"""\
    -vcodec h264 \
    {output_file} \
    """


def launch_stream(config: dict, output_directory: str):
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

    Get USB Resolutions:
        - lsusb -s 001:002 -v | egrep "Width|Height"
        - v4l2-ctl -d /dev/video0 --list-formats-ext
    """
    output_hls_file = os.path.join(output_directory, f'{config.name}.m3u8')
    output_mp4_file = os.path.join(output_directory, f'{config.name}.mp4')

    input = get_video_input()
    encoding = get_tuned_encoding_pipeline(config.config)
    output_hls = get_hls_output_pipeline(config.config, output_hls_file)

    command = f"ffmpeg {input} {encoding} {output_hls}"

    logger.info(f'Running ffmpeg pipeline: {command}')

    if state.get_global_setting('debug'):
        return subprocess.Popen(command, shell=True)
    
    return subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class USBStream(TService):

    def __init__(self, config):
        super().__init__()
        self.set_interval(1E9)
        self.config = config
        self.process = None


    def run_start(self):
        output_dir = state.get_global_setting('stream_dir')
        clean_up_stream(self.config.name, output_dir)
        self.process = launch_stream(self.config, output_dir)


    def run_loop(self):
        if self.process.poll():
            self.stop()
    

    def run_end(self):
        clean_up_stream(self.config.name, state.get_global_setting('stream_dir'))
