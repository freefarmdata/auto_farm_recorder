import time
import os
import eventlet
from eventlet.green import socket
import socketio
from threading import Thread
from multiprocessing import Queue
from flask import Flask, request, send_file, send_from_directory

http_server = Flask(__name__)
socket_server = socketio.Server(
    logger=True,
    async_mode='threading',
    engineio_logger=True,
    cors_allowed_origins='*'
)

buffer_size = 1024*8

@socket_server.on('connect')
def connect(sid, environ):
    print('connect ', sid)
    return True

@socket_server.on('buffer')
def connect(sid, value):
    global buffer_size
    print('buffer ', value)
    buffer_size = int(value)
    return True

@socket_server.on('disconnect')
def disconnect(sid):
    print('disconnect ', sid)
    return True

@http_server.route('/', methods=['GET'])
def get_web():
    return send_file('./web/view-stream.html')


@http_server.route('/<string:file_name>', methods=['GET'])
def get_web_stuff(file_name):
    full_path = os.path.abspath('./web')
    return send_from_directory(directory=full_path, filename=file_name)


@http_server.route('/stream', methods=['POST'])
def stream_video():
    global buffer_size
    while True:
        buffer = request.stream.read(buffer_size)
        if len(buffer) <= 0:
            return 'OK', 200
        print(f'recieving and emitting data: {len(buffer)}')
        socket_server.emit('stream', data=buffer)


def start_socket_server():
    socket_port = 8082
    server = Flask(__name__)
    server.wsgi_app = socketio.WSGIApp(socket_server, server.wsgi_app)
    server.run(host='0.0.0.0', port=socket_port, threaded=True)
    # eventlet.wsgi.server(
    #     eventlet.listen(('0.0.0.0', socket_port)),
    #     socketio.WSGIApp(socket_server)
    # )

def start_http_server():
    stream_port = 8081
    http_server.run(host='0.0.0.0', port=stream_port, threaded=True)


if __name__ == "__main__":
    t1 = Thread(target=start_socket_server, daemon=True)
    t2 = Thread(target=start_http_server, daemon=True)
    t1.start()
    t2.start()

    while True:
        time.sleep(1)

    
    