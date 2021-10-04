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


    def run_start(self):
        alarm_controller.clear_alarm('heartbeat_service_offline')


    def run_end(self):
        alarm_controller.set_warn_alarm('heartbeat_service_offline', 'Heartbeat Service Is Offline')


    @profile_func(name='heartbeat_loop')
    def run_loop(self):
        total, used, free = shutil.disk_usage("/")

        packet = {
            'disk_space_usage': round(used * 1E-6, 2),
            'disk_space_total': round(total * 1E-6, 2),
            'disk_space_free': round(free * 1E-6, 2),
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent
        }

        state.update_trigger('web_publisher', ('web/heartbeat/stats', packet))
        state.update_trigger('web_publisher', ('web/heartbeat/status', state.get_services_status()))