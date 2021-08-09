import time
import os
import argparse
import multiprocessing
import logging

from services.streamer import Streamer
from api import API
import setup_log

from fservice import state

logger = logging.getLogger()

def attach_streams():
  usb_default_config = {
    'camera_type': 'usb',
    'stream_name': 'back_cam',
    'crf': 35,
    'fontsize': 50,
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
    'hls_time': 0.5,
  }

  esp_default_config = {
    'camera_type': 'esp32',
    'stream_name': 'back_cam',
    'ip': '192.168.0.170',
    'crf': 23,
    'vsync': 2,
    'fontsize': 50,
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
  state.update_service('streamer', { 'action': 'attach', 'config': esp_default_config })


def initialize_settings(args):
  global settings

  sunrise = '6:0:0:0'
  sunset = '18:0:0:0'
  data_directory = '/usr/src/app/bin'

  if args.get('local') is True:
      data_directory = './bin'

  stream_directory = os.path.join(data_directory, 'streams')
  video_directory = os.path.join(data_directory, 'videos')

  os.makedirs(data_directory, exist_ok=True)
  os.makedirs(video_directory, exist_ok=True)
  os.makedirs(stream_directory, exist_ok=True)

  state.set_global_setting('debug', args.get('debug'))
  state.set_global_setting('local', args.get('local'))
  state.set_global_setting('data_dir', data_directory)
  state.set_global_setting('stream_dir', stream_directory)
  state.set_global_setting('video_dir', video_directory)
  state.set_global_setting('sunrise', sunrise)
  state.set_global_setting('sunset', sunset)


if __name__ == "__main__":
  multiprocessing.set_start_method('spawn', force=True)

  parser = argparse.ArgumentParser()
  parser.add_argument("--local", action="store_true", default=False)
  parser.add_argument("--debug", action="store_true", default=False)
  args = parser.parse_args().__dict__

  setup_log.setup_logger(args.get('debug'))

  state.register_service('streamer', Streamer)

  initialize_settings(args)

  state.start_services()

  attach_streams()

  api = API()
  api.start()

  try:
    while True:
      time.sleep(1000)
  except:
    state.stop_services()

  logger.info('streamer exiting')



