from dataclasses import dataclass

config = None

@dataclass(frozen=True)
class Config():
    local: bool
    debug: bool
    record: bool
    stream_dir: str
    socket_port: int


def get_config():
    global config
    return config


def setup_config(args):
    global config
    
    config = Config(
        local=args.local,
        debug=args.debug,
        record=args.record,
        stream_dir='./bin/streamer/videos',
        socket_port=5454
    )