import datetime
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
from util.time_util import sec_to_date

import controllers.settings as settings_controller

from services.mock_mqtt import MockMQTT
from services.mqtt_board import MQTTBoard
from services.heartbeat import Heartbeat
from services.streamer import Streamer
from services.uploader import Uploader
from services.archiver import Archiver

from triggers.web_publisher import WebPublisher

logger = logging.getLogger()


def create_directories(args):
  data_directory = '/usr/src/app/bin'
  if args.get('local') is True:
    data_directory = './bin/recorder' 

  image_directory = os.path.join(data_directory, 'images')
  video_directory = os.path.join(data_directory, 'videos')
  model_directory = os.path.join(data_directory, 'model')
  stream_directory = os.path.join(data_directory, 'streams')
  archive_directory = os.path.join(data_directory, 'archive')

  os.makedirs(data_directory, exist_ok=True)
  os.makedirs(image_directory, exist_ok=True)
  os.makedirs(video_directory, exist_ok=True)
  os.makedirs(archive_directory, exist_ok=True)
  os.makedirs(model_directory, exist_ok=True)
  os.makedirs(stream_directory, exist_ok=True)

  state.set_global_setting('data_dir', data_directory)
  state.set_global_setting('image_dir', image_directory)
  state.set_global_setting('video_dir', video_directory)
  state.set_global_setting('archive_dir', archive_directory)
  state.set_global_setting('model_dir', model_directory)
  state.set_global_setting('stream_dir', stream_directory)
  state.set_global_setting('video_dir', video_directory)


def set_default_settings(args):
  localhost = '127.0.0.1'
  bucket_name = 'jam-general-storage'
  upload_path = 'datasets/auto_farm/test_experiment'
  sunrise = '6:0:0:0' 
  sunset = '18:0:0:0'
  resolution = [1920, 1080]
  soil_threshold = 500
  camera_interval = 60E9
  pano_interval = 1800E9 # 30 minutes
  upload_concurrency = 10
  mqtt_boards = ['mock_client']
  mqtt_metrics = ['soil', 'dsb_temp', 'dht11_temp', 'dht11_humid', 'bmp_temp', 'bmp_pressue', 'light']
  start_date = sec_to_date(time.time()).timestamp()
  expire_time = 7 * 24 * 60 * 60 # 7 days in seconds

  usb_default_config = {
    'camera_type': 'usb',
    'stream_name': 'frontcam',
    'aspect_ratio': 8/3,
    'video_index': 0,
    'threads': 1,
    'infps': 30,
    'outfps': 20,
    'outres': '1280x720',
    'inres': '1280x720',
    'vsync': 1,
    'bitrate': '512k',
    'segment_time': 30,
    'stream_host': '0.0.0.0',
    'stream_port': 8083,
  }

  esp_default_config = {
    'camera_type': 'esp32',
    'stream_name': 'backcam',
    'ip_address': '192.168.0.102',
    'aspect_ratio': 4/3,
    'threads': 1,
    'infps': 30,
    'outfps': 20,
    'outres': '1024x768',
    'inres': '1024x768',
    'vsync': 1,
    'bitrate': '512k',
    'segment_time': 30,
    'stream_host': '0.0.0.0',
    'stream_port': 8083,
  }

  database_host = localhost if args.get('local') else 'postgres'
  mqtt_host = localhost if args.get('local') else 'mosquitto'

  state.set_global_setting('sunrise', sunrise)
  state.set_global_setting('sunset', sunset)
  state.set_global_setting('debug', args.get('debug'))
  state.set_global_setting('local', args.get('local'))
  state.set_global_setting('database_host', database_host)
  state.set_global_setting('mqtt_host', mqtt_host)
  state.set_global_setting('start_date', start_date)

  state.set_service_setting('mqtt_board', 'boards', mqtt_boards)
  state.set_service_setting('mqtt_board', 'metrics', mqtt_metrics)
  state.set_service_setting('usb_camera', 'interval', camera_interval)
  state.set_service_setting('usb_camera', 'resolution', resolution)
  state.set_service_setting('video', 'resolution', resolution)
  state.set_service_setting('uploader', 'upload_path', upload_path)
  state.set_service_setting('uploader', 'bucket_name', bucket_name)
  state.set_service_setting('uploader', 'concurrency', upload_concurrency)
  state.set_service_setting('archiver', 'expire_time', expire_time)
  state.set_service_setting('archiver', 'last_archive', None)

  state.set_service_setting('soil_predictor', 'threshold', soil_threshold)
  state.set_service_setting('panorama', 'pano_interval', pano_interval)
  state.set_service_setting('streamer', 'streams', [usb_default_config, esp_default_config])


if __name__ == "__main__":
  multiprocessing.set_start_method('spawn', force=True)
  parser = argparse.ArgumentParser()
  parser.add_argument("--local", action="store_true", default=False)
  parser.add_argument("--debug", action="store_true", default=False)
  args = parser.parse_args().__dict__

  setup_log.setup_logger(args.get('debug'))

  if args.get('local'):
    state.register_service('mock_mqtt', MockMQTT)

  state.register_service('mqtt_board', MQTTBoard)
  state.register_service('heartbeat', Heartbeat)
  state.register_service('streamer', Streamer)
  state.register_service('uploader', Uploader)
  state.register_service('archiver', Archiver)

  state.register_trigger('web_publisher', WebPublisher)

  create_directories(args)
  set_default_settings(args)
  settings_controller.load_settings()
  
  settings = state.get_all_settings()

  logger.info(f"recorder launched with settings: {settings}")

  database.initialize()

  API().start()
  state.start_triggers()
  state.start_services()

  try:
    while True:
      time.sleep(1000)
  except:
    state.stop_services()
    state.stop_triggers()