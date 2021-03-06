import json
import database
import requests
import logging

from paho.mqtt.client import mqtt

from util.time_util import profile_func
from util.tservice import TService
import controllers.alarms as alarm_controller
import state

logger = logging.getLogger()


def on_message(mqtt_client, userdata, message):
  logger.info(f'board message recieved: {message}')


class MQTTBoard(TService):


  def __init__(self):
    super().__init__()
    self.set_interval(5E9)
    self.mqtt_client = None


  def run_start(self):
    alarm_controller.clear_alarm('mqtt_board_service_offline')
    self.mqtt_client = mqtt.Client()
    self.mqtt_client.connect('mosquitto')
    self.mqtt_client.subscribe('board/*')
    self.mqtt_client.on_message = on_message
    self.mqtt_client.loop_start()


  def run_end(self):
    alarm_controller.set_warn_alarm('mqtt_board_service_offline', 'MQTTBoard Service Is Offline')
    self.mqtt_client.loop_stop()
    self.mqtt_client.disconnect()


  @profile_func(name='mqtt_board_loop')
  def run_loop(self):
    pass