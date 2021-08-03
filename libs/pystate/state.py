import os
import time
import json
import threading
import logging

logger = logging.getLogger(__name__)

settings = {}
services = {}

_setting_lock = threading.Lock()

def register_service(service_name, instance):
  global services
  if service_name in services:
    raise Exception(f'{service_name} already exists in services')

  if service_name == 'global':
    raise Exception(f'global is a reserved service name')
  
  services[service_name] = {
    'lock': threading.Lock(),
    'create': instance,
    'instance': None,
    'settings': {},
  }


def get_services_status():
  global services
  status = {}
  for service_name in services:
    status[service_name] = False
    with services[service_name]['lock']:
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
  if service_name in services:
    with services[service_name]['lock']:
      if services[service_name]['instance'] is None:

        if services[service_name]['settings'].get('disabled'):
          logger.info(f'Service {service_name} is disabled')
          return

        services[service_name]['instance'] = services[service_name]['create']()
        services[service_name]['instance'].start()


def stop_services():
  global services
  for service_name in services:
    with services[service_name]['lock']:
      logger.info(f'Stop service {service_name}')
      if services[service_name]['instance'] is not None:
        services[service_name]['instance'].stop()
  for service_name in services:
    with services[service_name]['lock']:
      if services[service_name]['instance'] is not None:
        while not services[service_name]['instance'].is_stopped():
          time.sleep(0.01)
      services[service_name]['instance'] = None
      logger.info(f'Service {service_name} stopped!')


def stop_service(service_name):
  global services
  logger.info(f'Stop service {service_name}')
  if service_name in services:
    with services[service_name]['lock']:
      if services[service_name]['instance'] is not None:
        services[service_name]['instance'].stop()
        while not services[service_name]['instance'].is_stopped():
          time.sleep(0.01)
        services[service_name]['instance'] = None
        logger.info(f'Service {service_name} stopped!')


def update_service(service_name, message):
  global services
  logger.info(f'Update service {service_name}: {message}')
  if service_name in services:
    with services[service_name]['lock']:
      if services[service_name]['instance'] is not None:
        services[service_name]['instance'].update(message)


def set_global_setting(key, value):
  global settings
  with _setting_lock:
    settings[key] = value


def get_global_setting(key):
  global settings
  with _setting_lock:
    return settings.get(key)


def set_service_setting(service_name, key, value):
  global services
  if service_name in services:
    with services[service_name]['lock']:
      services[service_name]['settings'][key] = value


def get_service_setting(service_name, key):
  global services
  if service_name in services:
    with services[service_name]['lock']:
      if key in services[service_name]['settings']:
        return services[service_name]['settings'][key]


def get_service_settings(service_name):
  global services
  if service_name in services:
    with services[service_name]['lock']:
      return services[service_name]['settings']

  
def get_all_settings():
  global services, settings
  with _setting_lock:
    returned = { 'global': settings }
  for service_name in services:
    with services[service_name]['lock']:
      returned[service_name] = services[service_name].get('settings', {})
  return returned