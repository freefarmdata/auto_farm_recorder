import os
from threading import Thread
import time
import logging
import argparse
import socket
from timeit import default_timer as timer

from flask import Flask, send_from_directory
from flask.helpers import send_file
import socketio

from setup_log import setup_logger
from controllers import clients
from stream_process import StreamProcess
from config import setup_config, get_config

logger = logging.getLogger()

flask_server = Flask(__name__)
socket_server = socketio.Server(
    logger=False,
    async_mode='threading',
    engineio_logger=False,
    cors_allowed_origins='*'
)

@socket_server.on('connect')
def connect(sid, environ):
    clients.add_client(sid)
    return True


@socket_server.on('request_stream')
def request_stream(sid, stream_name):
    socket_server.enter_room(sid, stream_name)
    clients.attach_stream(sid, stream_name)
    return True


@socket_server.on('exit_stream')
def exit_stream(sid, stream_name):
    socket_server.leave_room(sid, stream_name)
    clients.detach_stream(sid, stream_name)
    return True


@socket_server.on('disconnect')
def disconnect(sid):
    clients.delete_client(sid)
    return True


@flask_server.route('/web/<string:file_name>', methods=['GET'])
def get_web_files(file_name):
    web_dir = os.path.abspath('./src/web')
    return send_from_directory(directory=web_dir, filename=file_name)


@flask_server.route('/web', methods=['GET'])
def get_web():
    return send_file(os.path.abspath('./src/web/view-stream.html'))


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


def launch_server():
    config = get_config()
    flask_server.wsgi_app = socketio.WSGIApp(socket_server, flask_server.wsgi_app)
    flask_server.run(host='0.0.0.0', port=config.socket_port, threaded=True)


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
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--local", action="store_true", default=False)
    parser.add_argument("--debug", action="store_true", default=False)
    parser.add_argument("--record", action="store_true", default=False)
    args = parser.parse_args()

    setup_config(args)
    setup_logger(debug=get_config().debug)

    os.makedirs(get_config().stream_dir, exist_ok=True)

    usb_default_config = {
        'camera_type': 'usb',
        'stream_name': 'frontcam',
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
        'stream_port': 8083,
    }

    esp_default_config = {
        'camera_type': 'esp32',
        'stream_name': 'backcam',
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
    
    server = Thread(target=launch_server, daemon=True)
    server.start()

    for stream_config in stream_configs:
        stream = StreamProcess(stream_config)
        stream.start()
        streams.append(stream)
        relay = Thread(target=launch_relay, args=(stream_config,), daemon=True)
        relay.start()

    while True:
        for index in range(len(streams)):
            if not streams[index].is_alive():
                stream = StreamProcess(streams[index].stream_config)
                stream.start()
                streams[index] = stream
        time.sleep(5)