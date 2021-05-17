from flask_socketio import emit
import time
import json
from enum import Enum
import threading

from api import app


alarm_dict = {}
_alarm_lock = threading.Lock()


def get_active_alarms():
    global alarm_dict
    with _alarm_lock:
        active_alarms = {}
        for alarm_id in alarm_dict:
            if alarm_dict[alarm_id]['active']:
                active_alarms[alarm_id] = alarm_dict[alarm_id]
        return active_alarms


def clear_alarm(alarm_id):
    global alarm_dict
    with _alarm_lock:
        if alarm_id in alarm_dict:
            alarm_dict[alarm_id]['active'] = False
            with app.app_context():
                emit('alarm', alarm_dict[alarm_id], namespace='/', broadcast=True)


def set_info_alarm(alarm_id, name, message=None):
    set_alarm(alarm_id, 'info', name, message)


def set_warn_alarm(alarm_id, name, message=None):
    set_alarm(alarm_id, 'warn', name, message)


def set_danger_alarm(alarm_id, name, message=None):
    set_alarm(alarm_id, 'danger', name, message)


def set_critcal_alarm(alarm_id, name, message=None):
    set_alarm(alarm_id, 'critical', name, message)


def set_alarm(alarm_id, level, name, message=None):
    global alarm_dict
    with _alarm_lock:
        alarm_dict[alarm_id] = {
            'id': alarm_id,
            'active': True,
            'level': level,
            'time': time.time(),
            'name': name,
            'message': message,
        }
        with app.app_context():
            emit('alarm', alarm_dict[alarm_id], namespace='/', broadcast=True)
