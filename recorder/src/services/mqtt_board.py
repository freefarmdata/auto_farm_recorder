import logging

from fservice import state
from fservice.tservice import TService
from paho.mqtt.client import mqtt

from util.time_util import profile_func
import controllers.alarms as alarm_controller

logger = logging.getLogger()


def on_message(mqtt_client, userdata, message):
  logger.info(f'board message recieved: {message}')


class MQTTBoard(TService):


  def __init__(self):
    super().__init__()
    self.set_interval(1E9)
    self.mqtt_client = None


  def run_start(self):
    alarm_controller.clear_alarm('mqtt_board_service_offline')
    self.mqtt_client = mqtt.Client(clean_session=False)
    self.mqtt_client.connect('mosquitto', port=1883)
    self.mqtt_client.subscribe('board/*')
    self.mqtt_client.on_message = on_message


  def run_end(self):
    alarm_controller.set_warn_alarm('mqtt_board_service_offline', 'MQTTBoard Service Is Offline')
    self.mqtt_client.disconnect()


  @profile_func(name='mqtt_board_loop')
  def run_loop(self):
    self.mqtt_client.loop(timeout=5.0)