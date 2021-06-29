import os
import time
import logging
import subprocess

from util.tservice import TService

logger = logging.getLogger()


def launch_stream(ip, name, output):
    """
    http://underpop.online.fr/f/ffmpeg/help/hls-2.htm.gz
    https://ffmpeg.org/ffmpeg-formats.html#hls-1

    """
    output_file = os.path.join(output, f'{name}.m3u8')

    command = f"""
        ffmpeg \
            -i http://{ip}:81/stream \
                -c:v libx264 \
                -crf 21 \
                -preset superfast \
                -r 30 \
                -g 30 \
            -f hls \
                -hls_flags append_list+delete_segments \
                -hls_playlist_type delete_segments \
                -hls_segment_type mpegts \
                -hls_allow_cache 0 \
                -hls_list_size 0 \
                -hls_time 4 \
                {output_file}
    """

    return subprocess.Popen(command)


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
        self.process = launch_stream(self.ip, self.name, output_dir)


    def run_loop(self):
        if self.process.poll():
            self.stop()
    

    def run_end():
        pass