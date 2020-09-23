import re
import subprocess
import datetime
import logging
from service import Service

MOTION_IS_ACTIVE = re.compile(r'^Active: active (running)')
MOTION_IS_INACTIVE = re.compile(r'^Active: inactive')

logger = logging.getLogger(__name__)

SUNRISE = datetime.time(5, 0, 0, 0)
SUNSET = datetime.time(19, 0, 0, 0)

class Camera(Service):

  def __init__(self):
    super().__init__()

  def run_start(self):
    self.set_interval(10E9)

  def run_loop(self):
    motion_is_active = self.is_motion_active()

    # Start motion if it's day
    if not motion_is_active and self.is_daytime():
      logger.info('Motion is not active during the day. Starting...')
      self.start_motion()

    # Stop motion if it's night
    elif motion_is_active and not self.is_daytime():
      logger.info('Motion is active during the night. Stopping...')
      self.stop_motion()

  def is_daytime(self):
    current_time = datetime.datetime.now().time()
    return current_time >= SUNRISE and current_time <= SUNSET

  def is_motion_active(self):
    try:
      command = ['service', 'motion', 'status', '|', 'grep', 'Active']
      output = subprocess.check_output(command, shell=True).decode("utf-8").strip()
      if re.match(MOTION_IS_ACTIVE, output):
        return True
      elif re.match(MOTION_IS_INACTIVE, output):
        return False
    except Exception as e:
      logger.error(f'Failed to check motion status: {str(e)}')

  def start_motion(self):
    try:
      subprocess.run('service motion start')
    except Exception as e:
      logger.error(f'Failed to start motion: {str(e)}')

  def stop_motion(self):
    try:
      subprocess.run('service motion stop')
    except Exception as e:
      logger.error(f'Failed to stop motion: {str(e)}')

  def restart_motion(self):
    try:
      subprocess.run('service motion restart')
    except Exception as e:
      logger.error(f'Failed to restart motion: {str(e)}')