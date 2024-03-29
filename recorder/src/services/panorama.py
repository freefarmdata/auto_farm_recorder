import logging
import time

from fservice import state
from fservice.tservice import TService
import paho.mqtt.client as mqtt

from util.time_util import profile_func
import controllers.panorama as panoc
import controllers.alarms as alarm_controller

logger = logging.getLogger()

state_tx_route = "/panorama/pano_1/state/tx"
state_rx_route = "/panorama/pano_1/state/rx"

class Panorama(TService):


  def __init__(self):
    super().__init__(name='panorama')
    self.set_interval(1E9)
    self.pano_running = False
    self.last_pano = time.time_ns()
    self.mqtt_client = mqtt.Client()


  def run_start(self):
    alarm_controller.clear_alarm('panorama_service_offline')
    host = state.get_global_setting('mqtt_host')
    self.mqtt_client.connect(host, port=1883)
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
      pano_code = panoc.compile_code(panoc.pano_state, [["angle", "5"]])
      self.mqtt_client.publish(state_rx_route, pano_code)


  def on_message(self):
    def on_mqtt_message(_, userdata, message):
      if message.topic == state_tx_route:
        self.on_state_tx_route(message)
  
    return on_mqtt_message
  
  def on_state_tx_route(self, message):
    codes = message.payload.decode()
    codes = panoc.parse_code(codes)

    for code in codes:
      if 'error' in code['settings']:
        alarm_controller.set_warn_alarm(
          'panorama_error_code',
          f"Error code: {code['settings']['error']} recieved"
        )