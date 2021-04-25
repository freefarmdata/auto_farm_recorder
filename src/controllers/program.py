from flask_socketio import emit
import threading
import copy
from datetime import datetime

import controllers.watering as water_controller

import state

_info_lock = threading.Lock()

web_data = {
    'status': {},
    'info': {
        'camera_settings': {},
        'watering_times': [],
        'soil_models': []
    },
    'tags': {
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
    }
}


def increment_tag_key(key, value):
    global web_data
    with _info_lock:
        if key not in web_data['tags']:
            web_data['tags'] = 0
        if web_data['tags'][key] is None:
            web_data['tags'][key] = 0
        web_data['tags'][key] += value


def get_tag_key(key):
    global web_data
    with _info_lock:
        return web_data['tags'][key]


def set_tag_key(key, value):
    global web_data
    with _info_lock:
        web_data['tags'][key] = value


def get_info_key(key):
    global web_data
    with _info_lock:
        return web_data['info'][key]


def set_info_key(key, value):
    global web_data
    with _info_lock:
        web_data['info'][key] = value


def get_web_data():
    global web_data
    with _info_lock:
        web_copy = copy.deepcopy(web_data)
        web_copy['status'] = state.get_services_status()
        web_copy['info']['camera_settings'] = state.get_service_settings('camera')
        web_copy['tags']['farm_start_time'] = datetime.fromtimestamp(web_copy['tags']['farm_start_time']).ctime()
        return web_copy