import time
import sys
import datetime
import signal
import state
import api
import database
import logger

def signal_handler(sig, frame):
  state.stop_services()
  sys.exit(0)
  exit(0)

if __name__ == "__main__":
  signal.signal(signal.SIGINT, signal_handler)

  # Twenty second delay start up for postgres
  time.sleep(20)

  logger.setup_logger()
  database.initialize()
  state.init_services()
  state.start_services()
  api.start()

  upload_path = 'datasets/auto_farm/experiment_hawaii_2021/images/'
  sunrise = datetime.time(6, 0, 0, 0)
  sunset = datetime.time(18, 0, 0, 0)
  resolution = (1920, 1080)
  camera_interval = 30E9

  state.set_on_service('camera', 'sunrise', sunrise)
  state.set_on_service('camera', 'sunset', sunset)
  state.set_on_service('camera', 'resolution', resolution)
  state.set_on_service('camera', '_interval', camera_interval)
  state.set_on_service('video', 'sunrise', sunrise)
  state.set_on_service('video', 'sunset', sunset)
  state.set_on_service('video', 'resolution', resolution)
  state.set_on_service('uploader', 'sunrise', sunrise)
  state.set_on_service('uploader', 'sunset', sunset)
  state.set_on_service('uploader', 'upload_path', upload_path)

  while True:
    time.sleep(100)