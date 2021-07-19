import time
import os
import argparse
import multiprocessing
import logging

from util.stream_config import StreamConfig
from api import API
import setup_log
import state

logger = logging.getLogger()

def attach_streams():
  usb_default_config = (
    StreamConfig
      .create()
      .with_type('usb')
      .with_name('front_cam')
  )

  esp_default_config = (
    StreamConfig
      .create()
      .with_type('esp32')
      .with_name('back_cam')
      .with_config({ 'ip': '192.168.0.170' })
  )

  state.update_service('streamer', { 'action': 'attach', 'config': usb_default_config })
  state.update_service('streamer', { 'action': 'attach', 'config': esp_default_config })


if __name__ == "__main__":
  multiprocessing.set_start_method('spawn', force=True)

  parser = argparse.ArgumentParser()
  parser.add_argument("--local", action="store_true", default=False)
  parser.add_argument("--debug", action="store_true", default=False)
  args = parser.parse_args().__dict__

  setup_log.setup_logger(args.get('debug'))

  state.initialize(args)

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



