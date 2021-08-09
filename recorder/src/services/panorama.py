import logging
import time

from fservice import state
from fservice.tservice import TService
from paho.mqtt.client import mqtt

from util.time_util import profile_func
import controllers.panorama as pano_controller
import controllers.alarms as alarm_controller

logger = logging.getLogger()

state_tx_route = "/panorama/pano_1/state/tx"
state_rx_route = "/panorama/pano_1/state/rx"

class Panorama(TService):


  def __init__(self):
    super().__init__()
    self.set_interval(1E9)
    self.pano_running = False
    self.last_pano = time.time_ns()
    self.state_machine = None
    self.mqtt_client = None


  def run_start(self):
    alarm_controller.clear_alarm('panorama_service_offline')
    self.mqtt_client = mqtt.Client(clean_session=False)
    self.mqtt_client.connect('mosquitto', port=1883)
    self.mqtt_client.subscribe('panorama/*')
    self.mqtt_client.on_message = self.on_message()


  def run_end(self):
    alarm_controller.set_warn_alarm('panorama_service_offline', 'Panorama Service Is Offline')


  @profile_func(name='panorama_loop')
  def run_loop(self):
    """
    Read current state of servo motor. Where is it?
    Position it back to the start. Normal position.
    Initialize camera. Is it online and working?
    Start process:
      - tick forward
      - take a picture
      - send the picture
      - verify image successful, if not, retake several times
      - If failure, emit alarm and exit code
      - repeat process X amount of times.
    Capture all images and create panorama
    Completion!
    """
    self.mqtt_client.loop(timeout=5.0)
    self.schedule_pano_image()


  def schedule_pano_image(self):
    interval = state.get_service_setting('panorama', 'pano_interval')

    if not self.pano_running and time.time_ns() - self.last_pano >= interval:
      self.pano_running = True
      self.last_pano = time.time_ns()
      self.state_machine = pano_controller.get_pano_state_machine()
      self.mqtt_client.publish(state_rx_route, pano_controller.get_pano_code(5))


  def on_message(self):
    def on_mqtt_message(_, userdata, message):
      if message.topic == state_tx_route:
        self.on_state_tx_route(message)
  
    return on_mqtt_message
  
  def on_state_tx_route(self, message):
    code = message.payload.decode()
    did_transition = self.state_machine.next(code)