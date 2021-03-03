import datetime
import threading

from flask import jsonify

import database

# controls whether watering is happening
watering = {
    'lock': threading.Lock(),
    'set': False,
    'start': None,
}


def get_water_time():
    global watering
    with watering.get('lock'):
        data = {'set': watering.get('set'), 'start': watering.get('start')}
        return jsonify(data), 200


def set_water_time():
    global watering
    with watering.get('lock'):
        if watering.get('set'):
            return 'Watering is already set', 400

        now = datetime.datetime.utcnow()

        watering['start'] = now
        watering['set'] = True

    return 'OK', 200


def clear_water_time():
    global watering
    with watering.get('lock'):
        if not watering.get('set'):
            return 'Watering is not set', 400

        now = datetime.datetime.utcnow()

        database.insert_watertime(watering.get('start'), now)

        watering['set'] = False
        watering['start'] = None

    return 'OK', 200
