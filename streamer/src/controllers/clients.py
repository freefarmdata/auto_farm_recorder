from socket_server import get_server


def stream_requested(stream_name):
    for socket in get_server().eio.sockets.copy().values():
        session = socket.session

        if stream_name in session['/']['streams']:
            print(f'socket {socket.sid} wants {stream_name}')
            return True

    return False


def anaylze_sockets():
    print(get_server().eio.sockets)
    for sid, socket in get_server().eio.sockets.copy().items():
        print('queue_size ->', sid, socket.queue.qsize())