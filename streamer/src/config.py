from dataclasses import dataclass

config = None

@dataclass(frozen=True)
class Config():
    local: bool
    debug: bool
    stream_dir: str
    socket_port: int


def get_config():
    global config
    return config


def setup_config():
    global config
    
    config = Config(
        local=True,
        debug=True,
        stream_dir='./bin/streamer/videos',
        socket_port=5454
    )