import serial
import json
import database
import logging
from util.service import Service
from util.board_manager import BoardManager

logger = logging.getLogger(__name__)

class Board(Service):


  def __init__(self):
    super().__init__()
    self.board_manager = BoardManager()


  def run_start(self):
    self.set_interval(1E9)


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
