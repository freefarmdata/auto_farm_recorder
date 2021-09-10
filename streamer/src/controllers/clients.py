from threading import Lock

_client_list = {}
list_lock = Lock()

def add_client(sid):
    with list_lock:
        if sid not in _client_list:
            _client_list[sid] = {}

def attach_stream(sid, stream_name):
    with list_lock:
        if sid in _client_list:
            _client_list[sid][stream_name] = True

def detach_stream(sid, stream_name):
    with list_lock:
        if sid in _client_list:
            del _client_list[sid][stream_name]

def stream_requested(stream_name):
    with list_lock:
        for sid in _client_list.keys():
            if stream_name in _client_list[sid]:
                return True
        return False

def delete_client(sid):
    with list_lock:
        if sid in _client_list:
            del _client_list[sid]