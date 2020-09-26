import cv2
import os
import datetime
import time
import logging
from service import Service

logger = logging.getLogger(__name__)

SUNRISE = datetime.time(5, 0, 0, 0)
SUNSET = datetime.time(23, 0, 0, 0)

def now_ms():
  return time.time()*1E3

class Camera(Service):

  def __init__(self):
    super().__init__()
    self.camera = None
    self.data_dir = '/etc/recorder'
    self.image_dir = os.path.join(self.data_dir, 'images')


  def run_start(self):
    self.set_interval(30E9)
    self.setup_data_dirs()
    self.setup_camera()


  def setup_data_dirs(self):
    if not os.path.isdir(self.data_dir):
      os.mkdir(self.data_dir)

    if not os.path.isdir(self.image_dir):
      os.mkdir(self.image_dir)


  def setup_camera(self):
    if self.camera is None:
      self.camera = cv2.VideoCapture(0)

      if not self.camera.isOpened():
        self.camera = None
        return

      self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
      self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 720)


  def shutdown_camera(self):
    if self.camera:
        self.camera.release()
    self.camera = None


  def run_loop(self):
    if not self.is_daytime():
      self.shutdown_camera()
      return

    self.setup_camera()
    self.capture_image()


  def is_daytime(self):
    current_time = datetime.datetime.now().time()
    return current_time >= SUNRISE and current_time <= SUNSET


  def capture_image(self):
    if self.camera:
      ret, frame = self.camera.read()
      if ret is True:
        file_name = f'{now_ms()}.png'
        file_path = os.path.join(self.image_dir, file_name)
        cv2.imwrite(file_path, frame)


  def is_motion_active(self):
    try:
      command = 'sudo service motion status | grep Active'
      output = subprocess.check_output(command, shell=True).decode("utf-8").strip()
      if re.match(MOTION_IS_ACTIVE, output):
        return True
      return False
    except Exception as e:
      logger.error(f'Failed to check motion status: {str(e)}')


  def start_motion(self):
    try:
      subprocess.run('sudo service motion start', shell=True)
    except Exception as e:
      logger.error(f'Failed to start motion: {str(e)}')


  def stop_motion(self):
    try:
      subprocess.run('sudo service motion stop', shell=True)
    except Exception as e:
      logger.error(f'Failed to stop motion: {str(e)}')


  def restart_motion(self):
    try:
      subprocess.run('sudo service motion restart', shell=True)
    except Exception as e:
      logger.error(f'Failed to restart motion: {str(e)}')