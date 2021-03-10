import datetime
import threading
import logging

from flask import jsonify

import state
import database

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

        now = datetime.datetime.utcnow()
        watering['start'] = now
        watering['set'] = True


def clear_water_time():
    global watering
    with watering.get('lock'):
        if not watering.get('set'):
            return

        try:
            database.insert_watertime(watering.get('start'), datetime.datetime.utcnow())
            trigger_retrain_soil_update()
            watering['set'] = False
            watering['start'] = None
        except:
            logger.exception(f'Failed to set watering time')


def trigger_retrain_soil_update():
    watering_times = database.query_latest_watering(amount=2)
    if len(watering_times) == 1:
        first_soil = database.query_for_first_soil()
        if first_soil:
            state.update_service('soil_predictor', {
                'action': 'train',
                'start_time': first_soil.get('timestamp'),
                'end_time': watering_times[0].get('start')
            })
    elif len(watering_times) == 2:
        state.update_service('soil_predictor', {
            'action': 'train',
            'start_time': watering_times[0].get('end'),
            'end_time': watering_times[1].get('start')
        })


def last_watering_times():
    return database.query_latest_watering(amount=2)