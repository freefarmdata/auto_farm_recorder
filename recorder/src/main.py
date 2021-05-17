import time
import os
import sys
import json
import datetime
import signal
import argparse
import multiprocessing
import logging

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import state
from api import API
import database
import setup_log

import controllers.alarms as alarm_controller
import controllers.program as program_controller

logger = logging.getLogger()


def create_directories(args):
  data_directory = '/etc/recorder' 
  if args.get('local') is True:
    data_directory = './bin/recorder' 

  image_directory = os.path.join(data_directory, 'images')
  video_directory = os.path.join(data_directory, 'videos')
  temp_directory = os.path.join(data_directory, 'temp')
  model_directory = os.path.join(data_directory, 'model')

  os.makedirs(data_directory, exist_ok=True)
  os.makedirs(image_directory, exist_ok=True)
  os.makedirs(video_directory, exist_ok=True)
  os.makedirs(temp_directory, exist_ok=True)
  os.makedirs(model_directory, exist_ok=True)

  state.set_global_setting('data_dir', data_directory)
  state.set_global_setting('image_dir', image_directory)
  state.set_global_setting('video_dir', video_directory)
  state.set_global_setting('temp_dir', temp_directory)
  state.set_global_setting('model_dir', model_directory)


def set_default_settings(args):
  bucket_name = 'jam-general-storage'
  upload_path = 'datasets/auto_farm/experiment_hawaii_2021/images/'
  sunrise = '6:0:0:0' 
  sunset = '18:0:0:0'
  resolution = [1920, 1080]
  soil_threshold = 500
  camera_interval = 0.05E9
  camera_save = 30E9

  state.set_global_setting('sunrise', sunrise)
  state.set_global_setting('sunset', sunset)
  state.set_global_setting('devmode', args.get('local'))

  state.set_service_setting('camera', 'save_frame', camera_save)
  state.set_service_setting('camera', 'interval', camera_interval)
  state.set_service_setting('camera', 'resolution', resolution)
  state.set_service_setting('video', 'resolution', resolution)
  state.set_service_setting('uploader', 'upload_path', upload_path)
  state.set_service_setting('uploader', 'bucket_name', bucket_name)
  state.set_service_setting('soil_predictor', 'threshold', soil_threshold)
  #state.set_service_setting('video', 'disabled', True)
  #state.set_service_setting('uploader', 'disabled', True)
  state.set_service_setting('soil_predictor', 'disabled', True)


def load_settings(args):
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


if __name__ == "__main__":
  multiprocessing.set_start_method('spawn', force=True)
  parser = argparse.ArgumentParser()
  parser.add_argument("--local", action="store_true", default=False)
  parser.add_argument("--debug", action="store_true", default=False)
  args = parser.parse_args().__dict__

  # Twenty second delay start up for postgres
  if args.get('local') is False:
    time.sleep(20)

  setup_log.setup_logger(args.get('debug'))

  #database.reset_all()
  database.initialize()
  create_directories(args)
  set_default_settings(args)
  load_settings(args)
  program_controller.set_tag_key('farm_start_time', time.time())

  alarm_controller.set_warn_alarm('video_service_offline', 'Video Service Is Offline')
  alarm_controller.set_warn_alarm('uploader_service_offline', 'Uploader Service Is Offline')
  alarm_controller.set_warn_alarm('heartbeat_service_offline', 'Heartbeat Service Is Offline')
  alarm_controller.set_warn_alarm('board_service_offline', 'Board Service Is Offline')
  alarm_controller.set_warn_alarm('camera_service_offline', 'Camera Service Is Offline')

  API().start()
  state.start_services()

  try:
    while True:
      time.sleep(1000)
  except:
    state.stop_services()
    pass
