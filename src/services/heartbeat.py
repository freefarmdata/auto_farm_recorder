import logging
import shutil
import time

import controllers.program as program_controller
from util.service import Service


logger = logging.getLogger(__name__)


class Heartbeat(Service):


    def __init__(self):
        super().__init__()
        self.set_interval(10e9)


    def run_loop(self):
        total, used, free = shutil.disk_usage("/")

        program_controller.set_info_key('disk_space_usage', used)
        program_controller.set_info_key('disk_space_total', total)
        program_controller.set_info_key('disk_space_free', free)

        farm_start_time = program_controller.get_info_key('farm_start_time')
        farm_up_time = time.time() - farm_start_time

        program_controller.set_info_key('farm_up_time', farm_up_time)


