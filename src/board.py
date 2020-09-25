import serial
import json
import database
import logging
from service import Service

logger = logging.getLogger(__name__)

class Board(Service):

  def __init__(self):
    super().__init__()
    self.port = '/dev/ttyUSB0'
    #self.port = '/dev/cu.usbserial-14130'
    #self.port = '/dev/cu.usbserial-A94JZL1H'
    self.baud_rate = 9600
    self.timeout = 2
    self.serial = None

  def run_start(self):
    self.set_interval(0.5E9)
    self.connect_to_board()

  def connect_to_board(self):
    try:
      self.serial = self.get_serial_port()
    except Exception as e:
      logger.error(f'Failed to connect to board: {str(e)}')
      self.serial = None

  def close_connection(self):
    if self.serial:
      self.serial.close()
    self.serial = None

  def run_loop(self):
    if self.serial is None:
      self.connect_to_board()
      return

    try:
      readings = self.read_sensors()
      self.save_sensor_data(readings)
      logger.info(f'Board Readings: {readings}')
    except Exception as e:
      logger.error(f'Failed to read from board: {str(e)}')
      self.close_connection()

  def save_sensor_data(self, readings):
    soil = []
    temp = []
    for reading in readings:
      if 'soil' in reading:
        for i,v in enumerate(reading.get('soil')):
          soil.append({'pin': i, 'value': v})
      if 'temp' in reading:
        for i,v in enumerate(reading.get('temp')):
          temp.append({'pin': i, 'value': v})
    database.insert_soil(soil)
    database.insert_temp(temp)

  def read_sensors(self):
    output = self.serial.read(1000).decode("utf-8")
    output = list(map(lambda l: l.strip(), output.split('\n')))
    messages = []
    for line in output:
      try:
        logger.info(f'Board Line: {line}')
        messages.append(json.loads(line))
      except Exception as e:
        pass
    return messages

  def get_serial_port(self):
    return serial.Serial(self.port, baudrate=self.baud_rate, timeout=self.timeout)