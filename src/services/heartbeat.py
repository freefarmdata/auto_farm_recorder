import serial
import json
import logging

from util.service import Service

logger = logging.getLogger(__name__)

class Heartbeat(Service):


    def __init__(self):
        super().__init__()
        self.set_interval(1E9)


    def run_loop(self):
        