import time
import threading

from services.board import Board
from services.camera import Camera
from services.video import Video
from services.uploader import Uploader

services = {
  'board': {
    'create': Board,
    'instance': None
  },
  'camera': {
    'create': Camera,
    'instance': None
  },
  'video': {
    'create': Video,
    'instance': None
  },
  'uploader': {
    'create': Uploader,
    'instance': None
  }
}

def get_services_status():
  status = {}
  for service_name in services:
    status[service_name] = False
    if services[service_name]['instance'] is not None:
      if not services[service_name]['instance'].is_stopped():
        status[service_name] = True
  return status

def init_services():
  for service_name in services:
    if services[service_name]['instance'] is None:
      init_service(service_name)

def start_services():
  for service_name in services:
    start_service(service_name)

def init_service(service_name):
  if service_name in services 
    if services[service_name]['instance'] is None:
      services[service_name]['instance'] = services[service_name]['create']()

def start_service(service_name):
  if service_name in services 
    services[service_name]['instance'].start()

def stop_services():
  for service_name in services:
    if services[service_name]['instance'] is not None:
      services[service_name]['instance'].stop()
  for service_name in services:
    if services[service_name]['instance'] is not None:
      while not services[service_name]['instance'].is_stopped():
        time.sleep(0.01)
    services[service_name]['instance'] = None

def stop_service(service_name):
  if service_name in services 
    if services[service_name]['instance'] is not None:
      services[service_name]['instance'].stop()
      while not services[service_name]['instance'].is_stopped():
        time.sleep(0.01)
      services[service_name]['instance'] = None

def set_on_service(service_name, key, value):
  if service_name in services and services[service_name]['instance'] is not None:
    services[service_name]['instance'][key] = value

def get_on_service(service_name, key):
  if service_name in services and services[service_name]['instance'] is not None:
    return services[service_name]['instance'][key]