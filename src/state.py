import time
import threading

from board import Board
from camera import Camera

_data_lock = threading.Lock()
_service_lock = threading.Lock()

services = {
  'board': {
    'create': Board,
    'instance': None
  },
  'camera': {
    'create': Camera,
    'instance': None
  }
}

def start_services():
  for service_name in services:
    if services[service_name]['instance'] is None:
      services[service_name]['instance'] = services[service_name]['create']()
      services[service_name]['instance'].start()

def stop_services():
  for service_name in services:
    if services[service_name]['instance'] is not None:
      services[service_name]['instance'].stop()
  for service_name in services:
    if services[service_name]['instance'] is not None:
      while not services[service_name]['instance'].is_stopped():
        time.sleep(0.1)
    services[service_name]['instance'] = None