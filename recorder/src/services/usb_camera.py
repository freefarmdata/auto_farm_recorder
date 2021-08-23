import cv2
import os
import datetime
import time
import logging

from fservice.tservice import TService
from fservice import state

import controllers.alarms as alarm_controller
from util.time_util import now_ms, get_daynight_schedule

logger = logging.getLogger()

class USBCamera(TService):


  def __init__(self):
    super().__init__(name='usb_camera')
    self.image_dir = state.get_global_setting('image_dir')
    self.sunrise, self.sunset = get_daynight_schedule(
        state.get_global_setting('sunrise'),
        state.get_global_setting('sunset')
    )
    self.camera = None

  
  def run_start(self):
    alarm_controller.clear_alarm('usb_camera_service_offline')
    self.set_interval(state.get_service_setting('usb_camera', 'interval'))


  def run_loop(self):
    if not self.is_daytime():
      self.shutdown_camera()
      alarm_controller.set_info_alarm('usb_camera_night_time', 'Shutting off usb camera for the night')
      return
      
    alarm_controller.clear_alarm('usb_camera_night_time')
    self.setup_camera()

    try:
      self.capture_image()
    except Exception as error:
      logger.exception('failed to capture image from usb camera')
      alarm_controller.set_warn_alarm('usb_camera_failed_capture', f'Failed to capture image: {error.message}')
      self.shutdown_camera()


  def run_end(self):
    alarm_controller.set_warn_alarm('usb_camera_service_offline', 'USBCamera Service Is Offline')


  def setup_camera(self):
    if self.camera is None:
      self.camera = cv2.VideoCapture(0)
      time.sleep(1)

      if not self.camera.isOpened():
        logger.error('Camera could not be opened')
        alarm_controller.set_danger_alarm('usb_camera_failed_open', 'Failed to start usb camera')
        self.camera = None
        return

      resolution = state.get_service_setting('usb_camera', 'resolution')
      self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
      self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])


  def shutdown_camera(self):
      if self.camera:
          self.camera.release()
      self.camera = None


  def is_daytime(self):
      current_time = datetime.datetime.now().time()
      return current_time >= self.sunrise and current_time <= self.sunset


  def capture_image(self):
      if self.camera:
          ret, frame = self.camera.read()
          if ret is True and frame is not None:
              file_name = f'{int(now_ms())}.png'
              file_path = os.path.join(self.image_dir, file_name)
              logger.info(f'captured and saving image: {file_path}')
              cv2.imwrite(file_path, frame)