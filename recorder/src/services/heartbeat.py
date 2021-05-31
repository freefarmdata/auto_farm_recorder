import logging
import psutil
import shutil
import datetime
import random
import time

import controllers.alarms as alarm_controller
import controllers.watering as water_controller
import controllers.soil_predictor as soil_controller
import controllers.program as program_controller
from util.tservice import TService
from util.time_util import profile_func

import state
import database


logger = logging.getLogger(__name__)


class Heartbeat(TService):


    def __init__(self):
        super().__init__()
        self.set_interval(3e9)


    def run_start(self):        
        soil_models = database.query_for_models()
        program_controller.set_info_key('soil_models', soil_models)

        watering_times = database.query_for_watering()
        program_controller.set_info_key('watering_times', watering_times)

        alarm_controller.clear_alarm('heartbeat_service_offline')


    def run_end(self):
        alarm_controller.set_warn_alarm('heartbeat_service_offline', 'Heartbeat Service Is Offline')


    @profile_func(name='heartbeat_loop')
    def run_loop(self):
        total, used, free = shutil.disk_usage("/")

        program_controller.set_tag_key('disk_space_usage', used * 1E-6)
        program_controller.set_tag_key('disk_space_total', total * 1E-6)
        program_controller.set_tag_key('disk_space_free', free * 1E-6)

        farm_start_time = program_controller.get_tag_key('farm_start_time')
        farm_up_time = time.time() - farm_start_time
        program_controller.set_tag_key('farm_up_time', str(datetime.timedelta(seconds=farm_up_time)))

        program_controller.set_tag_key('cpu_usage', psutil.cpu_percent())
        program_controller.set_tag_key('memory_usage', psutil.virtual_memory().percent)

        water_time = water_controller.get_water_time()
        water_start = water_time['start'].isoformat() if water_time['start'] is not None else None
        program_controller.set_tag_key('watering_set', water_time['set'])
        program_controller.set_tag_key('watering_start', water_start)
