import datetime
import threading

from flask import jsonify

import state
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

        database.insert_watertime(watering.get('start'), datetime.datetime.utcnow())

        trigger_retrain_soil_update()

        watering['set'] = False
        watering['start'] = None

    return 'OK', 200


def trigger_retrain_soil_update():
    watering_times = database.query_latest_watering(amount=2)

    if len(watering_times) == 1:
        first_soil = database.query_for_first_soil()
        if first_soil:
            state.update_serivce('soil_predictor', {
                'action': 'train',
                'start_time': first_soil.get('timestamp'),
                'end_time': watering_times[0].get('start')
            })
    elif len(watering_times) == 2:
        state.update_serivce('soil_predictor', {
            'action': 'train',
            'start_time': watering_times[0].get('end'),
            'end_time': watering_times[1].get('start')
        })


def last_watering_times():
    return database.query_latest_watering(amount=2)