import serial
import splex
from service import Service

class Camera(Service):

  def __init__(self):
    super().__init__()

  def run_start(self):
    self.set_interval(1E9)
    pass

  def run_loop(self):
    print('camera')
    pass