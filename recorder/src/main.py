import time
import os
import json
import argparse
import multiprocessing
import logging

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from fservice import state

from api import API
import database
import setup_log

from services.mock_mqtt import MockMQTT
from services.mqtt_board import MQTTBoard
from services.heartbeat import Heartbeat
from services.streamer import Streamer
from services.usb_camera import USBCamera

from triggers.board import BoardRelay
from triggers.alarms import AlarmNotifier

logger = logging.getLogger()


def create_directories(args):
  data_directory = '/usr/src/app/bin'
  if args.get('local') is True:
    data_directory = './bin/recorder' 

  image_directory = os.path.join(data_directory, 'images')
  video_directory = os.path.join(data_directory, 'videos')
  temp_directory = os.path.join(data_directory, 'temp')
  model_directory = os.path.join(data_directory, 'model')
  stream_directory = os.path.join(data_directory, 'streams')

  os.makedirs(data_directory, exist_ok=True)
  os.makedirs(image_directory, exist_ok=True)
  os.makedirs(video_directory, exist_ok=True)
  os.makedirs(temp_directory, exist_ok=True)
  os.makedirs(model_directory, exist_ok=True)
  os.makedirs(stream_directory, exist_ok=True)

  state.set_global_setting('data_dir', data_directory)
  state.set_global_setting('image_dir', image_directory)
  state.set_global_setting('video_dir', video_directory)
  state.set_global_setting('temp_dir', temp_directory)
  state.set_global_setting('model_dir', model_directory)
  state.set_global_setting('stream_dir', stream_directory)
  state.set_global_setting('video_dir', video_directory)


def set_default_settings(args):
  localhost = '127.0.0.1'
  bucket_name = 'jam-general-storage'
  upload_path = 'datasets/auto_farm/experiment_hawaii_2021/images/'
  sunrise = '6:0:0:0' 
  sunset = '18:0:0:0'
  resolution = [1920, 1080]
  soil_threshold = 500
  camera_interval = 60E9
  pano_interval = 1800E9 # 30 minutes
  mqtt_boards = ['mock_client']

  database_host = localhost if args.get('local') else 'postgres'
  mqtt_host = localhost if args.get('local') else 'mosquitto'

  state.set_global_setting('sunrise', sunrise)
  state.set_global_setting('sunset', sunset)
  state.set_global_setting('local', args.get('local'))
  state.set_global_setting('database_host', database_host)
  state.set_global_setting('mqtt_host', mqtt_host)

  state.set_service_setting('mqtt_board', 'boards', mqtt_boards)
  state.set_service_setting('usb_camera', 'interval', camera_interval)
  state.set_service_setting('usb_camera', 'resolution', resolution)
  state.set_service_setting('video', 'resolution', resolution)
  state.set_service_setting('uploader', 'upload_path', upload_path)
  state.set_service_setting('uploader', 'bucket_name', bucket_name)
  state.set_service_setting('soil_predictor', 'threshold', soil_threshold)
  state.set_service_setting('panorama', 'pano_interval', pano_interval)


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


def attach_streams():
  usb_default_config = {
    'camera_type': 'usb',
    'stream_name': 'front_cam',
    'crf': 35,
    'vsync': 2,
    'vcodec': 'copy',
    'video_size': '800x600',
    'minrate': '512k',
    'bufsize': '512k',
    'maxrate': '1M',
    'framerate': 30,
    'keyint_min': 120,
    'g': 120,
    'hls_list_size': 2,
    'hls_time': 1,
  }

  esp_default_config = {
    'camera_type': 'esp32',
    'stream_name': 'back_cam',
    'ip': '192.168.0.170',
    'crf': 23,
    'vsync': 2,
    'vcodec': 'copy',
    'video_size': '1024x768',
    'minrate': '512k',
    'bufsize': '512k',
    'maxrate': '1M',
    'framerate': 15,
    'keyint_min': 30,
    'g': 30,
    'hls_list_size': 2,
    'hls_time': 0.5,
  }

  state.update_service('streamer', { 'action': 'attach', 'config': usb_default_config })
  #state.update_service('streamer', { 'action': 'attach', 'config': esp_default_config })


if __name__ == "__main__":
  multiprocessing.set_start_method('spawn', force=True)
  parser = argparse.ArgumentParser()
  parser.add_argument("--local", action="store_true", default=False)
  parser.add_argument("--debug", action="store_true", default=False)
  args = parser.parse_args().__dict__

  # Twenty second delay start up for postgres
  if not args.get('local'):
    time.sleep(20)

  setup_log.setup_logger(args.get('debug'))

  if args.get('local'):
    state.register_service('mock_mqtt', MockMQTT)

  #state.register_service('usb_camera', USBCamera)
  state.register_service('mqtt_board', MQTTBoard)
  state.register_service('heartbeat', Heartbeat)
  state.register_service('streamer', Streamer)

  state.register_trigger('alarm_notifier', AlarmNotifier)
  state.register_trigger('board_relay', BoardRelay)

  create_directories(args)
  set_default_settings(args)
  load_settings(args)
  
  settings = state.get_all_settings()

  logger.info(f"recorder launched with settings: {settings}")

  database.reset_all()
  database.initialize()

  API().start()
  state.start_triggers()
  state.start_services()

  attach_streams()

  try:
    while True:
      time.sleep(1000)
  except:
    state.stop_services()
    state.stop_triggers()