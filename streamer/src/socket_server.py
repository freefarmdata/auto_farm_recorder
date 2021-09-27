import os
from threading import Thread
import time
import logging
import argparse
import socket
import queue
from timeit import default_timer as timer

from flask import Flask, app, send_from_directory
from flask_cors import CORS
from flask.helpers import send_file
import socketio

from config import get_config

logger = logging.getLogger()

flask_server = Flask(__name__)
CORS(flask_server, resources={r"*": {"origins": "*"}})

socket_server = None


def get_server():
    global socket_server
    return socket_server


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
    flask_server.run(host='0.0.0.0', port=5453, threaded=True)


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
        ping_interval=10,
        ping_timeout=5,
        http_compression=False,
        back_pressure_size=1000
    )

    @socket_server.on('connect')
    def connect(sid, environ):
        socket_server.save_session(sid, { 'streams': {} })
        return True


    @socket_server.on('play_stream')
    def play_stream(sid, stream_name):
        socket_server.enter_room(sid, stream_name)
        session = socket_server.get_session(sid)
        if stream_name not in session['streams']:
            session['streams'][stream_name] = True
        socket_server.save_session(sid, session)
        return True


    @socket_server.on('pause_stream')
    def pause_stream(sid, stream_name):
        socket_server.leave_room(sid, stream_name)
        session = socket_server.get_session(sid)
        if stream_name in session['streams']:
            del session['streams'][stream_name]
        socket_server.save_session(sid, session)
        return True


    @socket_server.on('disconnect')
    def disconnect(sid):
        return True
    