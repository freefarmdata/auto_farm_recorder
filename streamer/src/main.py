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

if __name__ == "__main__":
  multiprocessing.set_start_method('spawn', force=True)

  parser = argparse.ArgumentParser()
  parser.add_argument("--local", action="store_true", default=False)
  parser.add_argument("--debug", action="store_true", default=False)
  args = parser.parse_args().__dict__

  setup_log.setup_logger(args.get('debug'))

  state.initialize(args)

  state.start_services()

  default_config = StreamConfig.create().with_type('usb').with_name('default')

  state.update_service('streamer', { 'action': 'attach', 'config': default_config })

  api = API()
  api.start()

  try:
    while True:
      time.sleep(1000)
  except:
    state.stop_services()

  logger.info('streamer exiting')



