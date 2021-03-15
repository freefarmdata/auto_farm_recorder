from flask_socketio import emit
import threading
import copy
from datetime import datetime

import controllers.watering as water_controller

import state

_lock = threading.Lock()

web_data = {
    'info': {
        'next_water_prediction': None,
        'farm_start_time': None,
        'farm_up_time': None,
        'latest_soil_reading': None,
        'latest_pressure_reading': None,
        'latest_light_reading': None,
        'total_mb_uploaded': None,
        'total_mb_taken': None,
        'cpu_usage': None,
        'memory_usage': None,
        'disk_space_usage': None,
        'disk_space_total': None,
        'disk_space_free': None,
        'watering_set': None,
        'watering_start': None,
        'watering_times': [],
        'soil_models': []
    },
}


def increment_info_key(key, value):
    global web_data
    with _lock:
        if key not in web_data['info']:
            web_data['info'] = 0
        if web_data['info'][key] is None:
            web_data['info'][key] = 0
        web_data['info'][key] += value


def get_info_key(key):
    global web_data
    with _lock:
        return web_data['info'][key]


def set_info_key(key, value):
    global web_data
    with _lock:
        web_data['info'][key] = value


def get_web_data():
    global web_data
    with _lock:
        web_copy = copy.deepcopy(web_data)
        web_copy['status'] = state.get_services_status()
        web_copy['info']['farm_start_time'] = datetime.fromtimestamp(web_copy['info']['farm_start_time']).ctime()
        return web_copy