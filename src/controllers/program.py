from flask_socketio import emit
import threading
import datetime

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
        'total_bytes_uploaded': None,
        'total_bytes_taken': None,
        'disk_space_usage': None,
    },
    'status': None
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
        web_data['status'] = state.get_services_status()
        return web_data