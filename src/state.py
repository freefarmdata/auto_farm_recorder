import time
import threading
import logging

from services.board import Board
from services.camera import Camera
from services.video import Video
from services.uploader import Uploader
from services.heartbeat import Heartbeat
from services.soil_predictor import SoilPredictor

logger = logging.getLogger(__name__)

settings = {}

_service_lock = threading.Lock()

services = {
  'board': {
    'create': Board,
    'instance': None,
    'settings': {}
  },
  'camera': {
    'create': Camera,
    'instance': None,
    'settings': {}
  },
  'video': {
    'create': Video,
    'instance': None,
    'settings': {}
  },
  'uploader': {
    'create': Uploader,
    'instance': None,
    'settings': {}
  },
  'heartbeat': {
    'create': Heartbeat,
    'instance': None,
    'settings': {}
  },
  'soil_predictor': {
    'create': SoilPredictor,
    'instance': None,
    'settings': {}
  }
}


def get_services_status():
  global services
  status = {}
  with _service_lock:
    for service_name in services:
      status[service_name] = False
      if services[service_name]['instance'] is not None:
        if not services[service_name]['instance'].is_stopped():
          status[service_name] = True
  return status


def start_services():
  global services
  for service_name in services:
    start_service(service_name)


def start_service(service_name):
  global services
  logger.info(f'Start service {service_name}')
  with _service_lock:
    if service_name in services:
      if services[service_name]['instance'] is None:
        services[service_name]['instance'] = services[service_name]['create']()
        services[service_name]['instance'].start()


def stop_services():
  global services
  with _service_lock:
    for service_name in services:
      logger.info(f'Stop service {service_name}')
      if services[service_name]['instance'] is not None:
        services[service_name]['instance'].stop()
    for service_name in services:
      if services[service_name]['instance'] is not None:
        while not services[service_name]['instance'].is_stopped():
          time.sleep(0.01)
      services[service_name]['instance'] = None
      logger.info(f'Service {service_name} stopped!')


def stop_service(service_name):
  global services
  logger.info(f'Stop service {service_name}')
  with _service_lock:
    if service_name in services:
      if services[service_name]['instance'] is not None:
        services[service_name]['instance'].stop()
        while not services[service_name]['instance'].is_stopped():
          time.sleep(0.01)
        services[service_name]['instance'] = None
        logger.info(f'Service {service_name} stopped!')


def update_serivce(service_name, message):
  global services
  logger.info(f'Update service {service_name}: {message}')
  with _service_lock:
    if service_name in services:
      if services[service_name]['instance'] is not None:
        services[service_name]['instance'].update(message)


def set_global_setting(key, value):
  global settings
  settings[key] = value


def get_global_setting(key):
  global settings
  return settings[key]


def set_service_setting(service_name, key, value):
  global services
  if service_name in services:
    services[service_name]['settings'][key] = value


def get_service_setting(service_name, key):
  global services
  if service_name in services:
    return services[service_name]['settings'][key]
