import datetime
import threading
import logging

from flask import jsonify

import state
import database

import controllers.program as program_controller

logger = logging.getLogger(__name__)

# controls whether watering is happening
watering = {
    'lock': threading.Lock(),
    'set': False,
    'start': None,
}


def get_water_time():
    global watering
    with watering.get('lock'):
        return {
            'set': watering.get('set'),
            'start': watering.get('start')
        }


def set_water_time():
    global watering
    with watering.get('lock'):
        if watering.get('set'):
            return

        now = datetime.datetime.now()
        watering['start'] = now
        watering['set'] = True


def clear_water_time():
    global watering
    with watering.get('lock'):
        if not watering.get('set'):
            return

        try:
            database.insert_watertime(watering.get('start'), datetime.datetime.now())
            watering['set'] = False
            watering['start'] = None
            program_controller.set_info_key('watering_times', database.query_for_watering())
        except:
            logger.exception(f'Failed to set watering time')
