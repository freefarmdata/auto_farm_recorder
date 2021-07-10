import time
import os
import argparse
import multiprocessing
import logging

from api import API
from streamer import Streamer
import setup_log

logger = logging.getLogger()

def initialize(args):
  sunrise = '6:0:0:0'
  sunset = '18:0:0:0'
  data_directory = '/usr/src/app/bin'
  streams = [{
    'ip': '192.168.0.170',
    'name': 'front_box'
  }, {
    'ip': '192.168.0.102',
    'name': 'back_box',
  }]

  if args.get('local') is True:
    data_directory = './bin'

  temp_directory = os.path.join(data_directory, 'temp')
  video_directory = os.path.join(data_directory, 'videos')

  os.makedirs(data_directory, exist_ok=True)
  os.makedirs(video_directory, exist_ok=True)
  os.makedirs(temp_directory, exist_ok=True)

  return {
    'data_dir': data_directory,
    'temp_dir': temp_directory,
    'video_dir': video_directory,
    'sunrise': sunrise,
    'sunset': sunset,
    'streams': streams
  }

if __name__ == "__main__":
  multiprocessing.set_start_method('spawn', force=True)

  parser = argparse.ArgumentParser()
  parser.add_argument("--local", action="store_true", default=False)
  parser.add_argument("--debug", action="store_true", default=False)
  args = parser.parse_args().__dict__

  setup_log.setup_logger(args.get('debug'))

  config = initialize(args)

  api = API(config)
  streamer = Streamer(config)

  api.start()
  streamer.start()

  try:
    while True:
      time.sleep(1000)
  except:
    logger.exception('stopping streamer')
    streamer.stop()
    api.join(timeout=3)

  logger.exception('streamer exiting')



