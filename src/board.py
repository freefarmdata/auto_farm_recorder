import serial
import json
import database
from service import Service

class Board(Service):

  def __init__(self):
    super().__init__()
    self.port = '/dev/cu.usbserial-14130' #'/dev/cu.usbserial-A94JZL1H'
    self.baud_rate = 9600
    self.timeout = 1
    self.serial = None

  def run_start(self):
    self.set_interval(0.5E9)
    self.connect_to_board()

  def connect_to_board(self):
    try:
      self.serial = self.get_serial_port()
    except Exception as e:
      self.serial = None

  def run_loop(self):
    if self.serial is None:
      self.connect_to_board()
      return

    readings = self.read_sensors()
    self.save_sensor_data(readings)

  def save_sensor_data(self, readings):
    soil = []
    for reading in readings:
      for i,v in enumerate(reading.get('soil')):
        soil.append({'pin': i, 'value': v})
    database.insert_soil(soil)

  def read_sensors(self):
    output = self.serial.read_until('\n').decode("utf-8")
    output = list(map(lambda l: l.strip(), output.split('\n')))
    messages = []
    for line in output:
      try:
        messages.append(json.loads(line))
      except Exception as e:
        pass
    return messages

  def get_serial_port(self):
    return serial.Serial(self.port, baudrate=self.baud_rate, timeout=self.timeout)