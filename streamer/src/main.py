import os
from threading import Thread
import time
import logging
import argparse
import socket
from timeit import default_timer as timer

import socketio

from setup_log import setup_logger
from controllers import clients
from stream_process import StreamProcess
from config import setup_config
import socket_server

logger = logging.getLogger()


def launch_relay(config: dict):
    stream_port = config.get('stream_port')
    stream_name = config.get('stream_name')
    stream_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    stream_socket.bind(('0.0.0.0', stream_port))
    stream_socket.setblocking(True)
    stream_socket.settimeout(1.0)

    while True:
        if not clients.stream_requested(stream_name):
            time.sleep(0.1)
            continue

        last_check = timer()
        while True:
            if timer() - last_check >= 10:
                last_check = timer()
                if not clients.stream_requested(stream_name):
                    break

            try:
                buffer, address = stream_socket.recvfrom(1024*16)
                if len(buffer) <= 0:
                    continue

                socket_server.emit(
                    f'stream/{stream_name}',
                    data=buffer,
                    room=stream_name,
                    ignore_queue=True
                )
            except socket.timeout:
                pass


if __name__ == "__main__":
    """
    Problem A:
        TCP Packet playback may be buffering as data is trying
        to be sent to the user and isn't able to keep up with the data ingestion.
        This will cause delays in the video were the playback will be several
        seconds off. How to solve? Can I measure the length of the internal buffer
        from the socket_server and if it gets over a certain length just ignore it?

    Problem B:
        Play, Pause, and Resume functionality. This should be in addition to stopping
        the playback via the socket.io routes of "exit_stream". I should add some sort of
        pause symbol and play symbol of the video itself for this. Need to just stop writing
        frames to the video player also.

    Problem C:
        Refresh functionality. The decoder sometimes doesn't start correctly. We should need
        to restart the stream if this happens. A page reload solves this. But I imagine there
        is a JSMPEG way to fix this.

    Problem D:
        Buffer data on the server side and then sent it out? Or just stream out whatever is returned
        from the UDP socket. Experiment with functionality on this.

    Problem E:
        ffmpeg vsync parameter seems to introduce some optimization. How? Why? Experiment and
        find out why.

    Problem F:
        The quality of the stream is nothing fancy. How hard can I push it? How big can I get
        the resolution? Experiment with this. What about grayscale video?

    Problem G:
        Measure the total amount of data transmitted on server side and client side. Graph it
        in D3.js and show over time.

    STEREO CAMERA SETTINGS:
        640x240@[60.000240 60.000240]fps
        640x240@[30.000030 30.000030]fps
        1280x480@[60.000240 60.000240]fps
        1280x480@[30.000030 30.000030]fps
        2560x720@[60.000240 60.000240]fps
        2560x720@[30.000030 30.000030]fps
        2560x960@[60.000240 60.000240]fps
        2560x960@[30.000030 30.000030]fps

    python3 src/main.py \
        --debug \
        --grayscale \
        --bitrate 3M \
        --minrate 3M \
        --bufsize 5M \
        --maxrate 6M \
        --resolution 1280x480 \
        --quality 50 \
        --infps 30 \
        --outfps 20 \
        --threads 4 \
        --vsync 1
        
    
    python3 src/main.py \
        --local \
        --debug \
        --grayscale \
        --bitrate 256k \
        --minrate 128k \
        --bufsize 1M \
        --maxrate 2M \
        --resolution 1280x720 \
        --vsync 0 \
        --framerate 30
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true", default=False)
    parser.add_argument("--debug", action="store_true", default=False)
    parser.add_argument("--record", action="store_true", default=False)
    parser.add_argument("--archive", action="store_true", default=False)
    parser.add_argument("--grayscale", action="store_true", default=False)
    parser.add_argument("--bitrate", dest='bitrate', default='256k')
    parser.add_argument("--minrate", dest='minrate', default='256k')
    parser.add_argument("--bufsize", dest='bufsize', default='256k')
    parser.add_argument("--maxrate", dest='maxrate', default='512k')
    parser.add_argument("--resolution", dest='resolution', default='1280x480')
    parser.add_argument("--infps", dest='infps', default='30')
    parser.add_argument("--outfps", dest='outfps', default='30')
    parser.add_argument("--quality", dest='quality', default='30')
    parser.add_argument("--threads", dest='threads', default='1')
    parser.add_argument("--vsync", dest='vsync', default='2')
    args = parser.parse_args()

    app_config = setup_config(args)

    setup_logger(debug=app_config.debug)

    os.makedirs(app_config.stream_dir, exist_ok=True)

    # 1280x720
    # 1280x480

    usb_default_config = {
        'camera_type': 'usb',
        'stream_name': 'frontcam',
        'archive': app_config.archive,
        'grayscale': app_config.grayscale,
        'video_index': 0,
        'threads': args.threads,
        'infps': args.infps,
        'outfps': args.outfps,
        'video_size': args.resolution,
        'vsync': args.vsync,
        'quality': args.quality,
        'bitrate': args.bitrate,
        'minrate': args.minrate,
        'bufsize': args.bufsize,
        'maxrate': args.maxrate,
        'segment_time': 30,
        'stream_host': '0.0.0.0',
        'stream_port': 8083,
    }

    esp_default_config = {
        'camera_type': 'esp32',
        'stream_name': 'backcam',
        'archive': app_config.archive,
        'ip_address': '192.168.0.102',
        'video_index': 0,
        'threads': 1,
        'framerate': 20,
        'video_size': '640x480',
        'quality': 21,
        'bitrate': '256k',
        'minrate': '256k',
        'bufsize': '512k',
        'maxrate': '512k',
        'segment_time': 30,
        'stream_host': '0.0.0.0',
        'stream_port': 8084,
    }

    stream_configs = [
        usb_default_config,
        #esp_default_config
    ]
    
    streams = []

    socket_server.initialize()
    socket_server.start()

    for stream_config in stream_configs:
        stream = StreamProcess(stream_config)
        stream.start()
        streams.append(stream)
        relay = Thread(target=launch_relay, args=(stream_config,), daemon=True)
        relay.start()

    try:
        while True:
            for index in range(len(streams)):
                if not streams[index].is_alive():
                    stream = StreamProcess(streams[index].stream_config)
                    stream.start()
                    streams[index] = stream
            time.sleep(5)
    except:
        pass
    finally:
        for stream in streams:
            stream.process.kill()