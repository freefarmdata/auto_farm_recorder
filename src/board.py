import serial
import splex
from service import Service

class Board(Service):

  def __init__(self):
    super().__init__()
    self.port = None
    self.baud_rate = 9600
    self.timeout = 1

  def run_start(self):
    self.set_interval(0.2E9)
    pass

  def run_loop(self):
    print('board')
    readings = self.parse_output(self.read_sensors())

  def parse_output(self, output):
    if output is not None:
      keymap = { 's': 'soil', 't': 'temp', 'h': 'humid' }
      return splex.parse(output, keymap)

  def read_sensors(self):
    with self.get_serial_port() as port:
      output = port.read_until('\n').decode("utf-8")
      if output.startswith('#') and output.endswith('#'):
        return output

  def get_serial_port(self):
    return serial.Serial(self.port, baudrate=self.baud_rate, timeout=self.timeout)