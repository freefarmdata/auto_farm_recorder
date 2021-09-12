import os
from threading import Thread
import time
import logging
import argparse
import socket
from timeit import default_timer as timer

from flask import Flask, app, send_from_directory
from flask.helpers import send_file
import socketio

from controllers import clients
from config import get_config

logger = logging.getLogger()

flask_server = Flask(__name__)
socket_server = None


@flask_server.route('/web/<string:file_name>', methods=['GET'])
def get_web_files(file_name):
    web_dir = os.path.abspath('./src/web')
    return send_from_directory(web_dir, file_name)


@flask_server.route('/web', methods=['GET'])
def get_web():
    return send_file(os.path.abspath('./src/web/view-stream.html'))


def emit(*args, **kwargs):
    socket_server.emit(*args, **kwargs)


def launch_server():
    config = get_config()
    flask_server.wsgi_app = socketio.WSGIApp(socket_server, flask_server.wsgi_app)
    flask_server.run(host='0.0.0.0', port=config.socket_port, threaded=True)


def start():
    server = Thread(target=launch_server, daemon=True)
    server.start()    


def initialize():
    global socket_server

    socket_server = socketio.Server(
        logger=False,
        async_mode='threading',
        engineio_logger=False,
        cors_allowed_origins='*',
        max_http_buffer_size=50000,
        http_compression=False
    )

    @socket_server.on('connect')
    def connect(sid, environ):
        clients.add_client(sid)
        return True


    @socket_server.on('play_stream')
    def play_stream(sid, stream_name):
        socket_server.enter_room(sid, stream_name)
        clients.attach_stream(sid, stream_name)
        return True


    @socket_server.on('pause_stream')
    def pause_stream(sid, stream_name):
        socket_server.leave_room(sid, stream_name)
        clients.detach_stream(sid, stream_name)
        return True


    @socket_server.on('disconnect')
    def disconnect(sid):
        clients.delete_client(sid)
        return True
    