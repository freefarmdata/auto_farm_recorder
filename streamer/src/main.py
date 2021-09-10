import os
from threading import Thread
import time
import logging
import subprocess
import socket
from timeit import default_timer as timer

from flask import Flask, send_from_directory
from flask.helpers import send_file
import socketio

from setup_log import setup_logger
from controllers import clients
from controllers import streams

logger = logging.getLogger()

local = True
debug = True
stream_dir = './bin/streamer/videos'
socket_port = 5454
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
            logger.debug(f'No clients requesting stream: {stream_name}')
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
                socket_server.emit(f'stream/{stream_name}', data=buffer, room=stream_name)
            except socket.timeout:
                pass


def launch_stream(config: dict):
    command = streams.get_pi_usb_encoding_pipeline(config, stream_dir)
    if local:
        command = streams.get_mac_webcam_encoding_pipeline(config, stream_dir)

    logger.info(f'Running ffmpeg pipeline: {command}')

    if debug:
        return subprocess.Popen(command, shell=True)
    
    return subprocess.Popen(command, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def launch_server():
    flask_server.wsgi_app = socketio.WSGIApp(socket_server, flask_server.wsgi_app)
    flask_server.run(host='0.0.0.0', port=socket_port, threaded=True)


if __name__ == "__main__":
    setup_logger(debug=debug)

    usb_default_config = {
        'camera_type': 'usb',
        'stream_name': 'frontcam',
        'video_index': 0,
        'threads': 1,
        'framerate': 20,
        'video_size': '640x480',
        'quality': 21,
        'bitrate': '512k',
        'minrate': '512k',
        'bufsize': '768k',
        'maxrate': '768k',
        'segment_time': 30,
        'stream_host': 'localhost',
        'stream_port': 8083,
    }
    
    server = Thread(target=launch_server, daemon=True)
    server.start()

    relay = Thread(target=launch_relay, args=(usb_default_config,), daemon=True)
    relay.start()

    stream = launch_stream(usb_default_config)

    while True:

        if stream.poll():
            stream.kill()
            stream = launch_stream(usb_default_config)

        time.sleep(1)