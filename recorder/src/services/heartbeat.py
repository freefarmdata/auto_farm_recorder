import logging
import psutil
import shutil

from paho.mqtt.client import mqtt
from fservice import state
from fservice.tservice import TService

import controllers.alarms as alarm_controller
import controllers.program as program_controller
from util.time_util import profile_func
import database

logger = logging.getLogger(__name__)


class Heartbeat(TService):


    def __init__(self):
        super().__init__()
        self.set_interval(5E9)
        self.mqtt_client = mqtt.Client()


    def run_start(self):
        alarm_controller.clear_alarm('heartbeat_service_offline')


    def run_end(self):
        alarm_controller.set_warn_alarm('heartbeat_service_offline', 'Heartbeat Service Is Offline')


    @profile_func(name='heartbeat_loop')
    def run_loop(self):
        total, used, free = shutil.disk_usage("/")

        messages = [
            { 'topic': 'recorder/disk_space_usage', 'payload': used * 1E-6 },
            { 'topic': 'recorder/disk_space_total', 'payload': total * 1E-6 },
            { 'topic': 'recorder/disk_space_free', 'payload': free * 1E-6 },
            { 'topic': 'recorder/cpu_usage', 'payload': psutil.cpu_percent() },
            { 'topic': 'recorder/memory_usage', 'payload': psutil.virtual_memory().percent },
        ]

        self.mqtt_client.multiple(messages, hostname='mosquitto')
