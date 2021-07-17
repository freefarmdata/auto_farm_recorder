from services.usb_stream import USBStream
from services.esp32_stream import ESP32Stream
from util.tservice import TService

stream_types = [
    'esp32',
    'usb'
]

class StreamConfig:


    def __init__(self):
        self.type = 'usb'
        self.name = 'default'
        self.config = {}


    @staticmethod
    def config_from(config) -> TService:
        if config.type == 'usb':
            return USBStream(config)
        elif config.type == 'esp32':
            return ESP32Stream(config)


    @staticmethod
    def create():
        return StreamConfig()


    def with_type(self, type: str):
        self.type = type
        return self


    def with_name(self, name: str):
        self.name = name
        return self


    def with_config(self, config: dict):
        self.config = config
        return self
