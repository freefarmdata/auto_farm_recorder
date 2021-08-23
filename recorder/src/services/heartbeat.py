import logging
import psutil
import shutil
import json

import paho.mqtt.client as mqtt
from fservice import state
from fservice.tservice import TService

import controllers.alarms as alarm_controller
from util.time_util import profile_func

logger = logging.getLogger(__name__)


class Heartbeat(TService):


    def __init__(self):
        super().__init__(name='heartbeat')
        self.set_interval(5E9)
        self.mqtt_client = mqtt.Client(transport='websockets')


    def run_start(self):
        alarm_controller.clear_alarm('heartbeat_service_offline')
        host = state.get_global_setting('mqtt_host')
        self.mqtt_client.connect_async(host, port=9001)
        self.mqtt_client.ws_set_options(path="/mqtt", headers=None)
        self.mqtt_client.loop_start()


    def run_end(self):
        alarm_controller.set_warn_alarm('heartbeat_service_offline', 'Heartbeat Service Is Offline')
        self.mqtt_client.loop_stop()
        self.mqtt_client.disconnect()


    @profile_func(name='heartbeat_loop')
    def run_loop(self):
        total, used, free = shutil.disk_usage("/")

        packet = {
            'disk_space_usage': used * 1E-6,
            'disk_space_total': total * 1E-6,
            'disk_space_free': free * 1E-6,
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent
        }

        self.mqtt_client.publish('web/heartbeat', json.dumps(packet))