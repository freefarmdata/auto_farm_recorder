import time
import threading

from fservice import state

from util.time_util import now_ms

alarm_cache = {}

_alarm_lock = threading.Lock()

priority_map = {
    'info': 4,
    'warn': 3,
    'danger': 2,
    'critical': 1,
}


def get_active_alarms():
    global alarm_cache
    with _alarm_lock:
        active_alarms = {}
        for alarm_id in alarm_cache:
            if alarm_cache[alarm_id]['active']:
                active_alarms[alarm_id] = alarm_cache[alarm_id]
        return active_alarms


def clear_alarm(alarm_id):
    global alarm_cache
    with _alarm_lock:
        if alarm_id in alarm_cache:
            alarm_cache[alarm_id]['active'] = False


def set_info_alarm(alarm_id, name, message=None):
    set_alarm(alarm_id, 'info', name, message)


def set_warn_alarm(alarm_id, name, message=None):
    set_alarm(alarm_id, 'warn', name, message)


def set_danger_alarm(alarm_id, name, message=None):
    set_alarm(alarm_id, 'danger', name, message)


def set_critcal_alarm(alarm_id, name, message=None):
    set_alarm(alarm_id, 'critical', name, message)


def set_alarm(alarm_id, level, name, message=None):
    global alarm_cache
    with _alarm_lock:
        alarm = {
            'id': alarm_id,
            'active': True,
            'level': level,
            'time': now_ms(),
            'name': name,
            'message': message,
        }
        alarm_cache[alarm_id] = alarm
        state.update_trigger('alarm_notifier')