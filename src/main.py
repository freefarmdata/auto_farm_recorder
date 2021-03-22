import time
import os
import sys
import datetime
import signal
import argparse

import controllers.program as program_controller

import state
import api
import database
import logger

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' 

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--local", action="store_true", default=False)
  args = parser.parse_args().__dict__

  # Twenty second delay start up for postgres
  if args.get('local') is False:
    time.sleep(20)

  logger.setup_logger()

  #database.reset_all()
  database.initialize()

  data_directory = '/etc/recorder' 
  if args.get('local') is True:
    data_directory = './bin/recorder' 

  image_directory = os.path.join(data_directory, 'images')
  video_directory = os.path.join(data_directory, 'videos')
  temp_directory = os.path.join(data_directory, 'temp')
  model_directory = os.path.join(data_directory, 'model')

  bucket_name = 'jam-general-storage'
  upload_path = 'datasets/auto_farm/experiment_hawaii_2021/images/'
  sunrise = datetime.time(6, 0, 0, 0)
  sunset = datetime.time(18, 0, 0, 0)
  resolution = (1920, 1080)
  soil_threshold = 500
  camera_interval = 30E9

  os.makedirs(data_directory, exist_ok=True)
  os.makedirs(image_directory, exist_ok=True)
  os.makedirs(video_directory, exist_ok=True)
  os.makedirs(temp_directory, exist_ok=True)
  os.makedirs(model_directory, exist_ok=True)

  state.set_global_setting('sunrise', sunrise)
  state.set_global_setting('sunset', sunset)
  state.set_global_setting('devmode', args.get('local'))
  state.set_global_setting('image_dir', image_directory)
  state.set_global_setting('video_dir', video_directory)
  state.set_global_setting('temp_dir', temp_directory)
  state.set_global_setting('model_dir', model_directory)

  state.set_service_setting('camera', 'resolution', resolution)
  state.set_service_setting('video', 'resolution', resolution)
  state.set_service_setting('uploader', 'upload_path', upload_path)
  state.set_service_setting('uploader', 'bucket_name', bucket_name)
  state.set_service_setting('soil_predictor', 'threshold', soil_threshold)

  #state.set_service_setting('video', 'disabled', True)
  #state.set_service_setting('uploader', 'disabled', True)
  state.set_service_setting('soil_predictor', 'disabled', True)

  program_controller.set_info_key('farm_start_time', time.time())

  state.start_services()
  api.start()

  try:
    while True:
      time.sleep(100)
  except KeyboardInterrupt:
    pass
  finally:
    state.stop_services()
    exit(0)