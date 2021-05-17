import serial
import json
import database
import logging

from util.time_util import profile_func
from util.tservice import TService
import controllers.alarms as alarm_controller
from controllers.board_manager import BoardManager

logger = logging.getLogger(__name__)

class Board(TService):


  def __init__(self):
    super().__init__()
    self.board_manager = BoardManager()
    self.set_interval(5E9)

  
  def run_start(self):
    alarm_controller.clear_alarm('board_service_offline')


  def run_end(self):
    self.board_manager.reset()
    alarm_controller.set_warn_alarm('board_service_offline', 'Board Service Is Offline')


  @profile_func(name='board_loop')
  def run_loop(self):
    if len(self.board_manager.boards) <= 0:
      self.board_manager.detect()
      return

    messages = self.board_manager.read()
    self.save_sensor_data(messages)

    logger.info(f'Board Messages: {messages}')


  def save_sensor_data(self, messages):
    metrics = {'soil': [], 'temp': [], 'light': [], 'pressure': []}
    for message in messages:
      for metric in metrics:
        if metric in message:
          for i,v in enumerate(message[metric]):
            metrics[metric].append({'sensor': i, 'value': v, 'board_id': message['id']})

    for metric in metrics:
      database.insert_timeseries(metric, metrics[metric])
