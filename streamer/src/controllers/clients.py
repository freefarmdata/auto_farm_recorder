from threading import Lock
from dataclasses import dataclass

@dataclass
class Client():
    sid: str
    stream: str


_client_list = {}
list_lock = Lock()


def add_client(sid):
    with list_lock:
        if sid not in _client_list:
            _client_list[sid] = Client(sid=sid, stream=None)


def attach_stream(sid, stream_name):
    with list_lock:
        if sid in _client_list:
            _client_list[sid].stream = stream_name


def detach_stream(sid, stream_name):
    with list_lock:
        if sid in _client_list:
            _client_list[sid].stream = None


def stream_requested(stream_name):
    with list_lock:
        for sid in _client_list.keys():
             if _client_list[sid].stream == stream_name:
                return True
        return False


def delete_client(sid):
    with list_lock:
        if sid in _client_list:
            del _client_list[sid]