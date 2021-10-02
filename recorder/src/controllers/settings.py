import os
import json
import logging

from fservice import state

logger = logging.getLogger()


def save_settings(settings):
  try:
    data_directory = state.get_global_setting('data_dir')
    settings_path = os.path.join(data_directory, 'settings.json')
    with open(settings_path, 'w') as f:
      json.dump(settings, f)
  except:
    logger.exception('failed to load settings from file')


def load_settings():
  try:
    data_directory = state.get_global_setting('data_dir')
    settings_path = os.path.join(data_directory, 'settings.json')
    settings = {}
    if os.path.exists(settings_path):
      with open(settings_path, 'r') as f:
        settings = json.load(f)
    
    logger.info(f'Loaded Settings: {settings}')

    for service_name in settings:
      for setting in settings[service_name]:
        if service_name == 'global':
          state.set_global_setting(setting, settings[service_name][setting])
        else:
          state.set_service_setting(service_name, setting, settings[service_name][setting])
  except:
    logger.exception('failed to load settings from file')