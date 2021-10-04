import logging
import random
import json

from fservice import state
from fservice.tservice import TService
import paho.mqtt.client as mqtt

from util.time_util import profile_func
import controllers.alarms as alarm_controller

logger = logging.getLogger()

class MockMQTT(TService):


  def __init__(self):
    super().__init__(name="mock_mqtt")
    self.set_interval(5E9)
    self.mqtt_client = mqtt.Client()


  def run_start(self):
    alarm_controller.clear_alarm('mock_mqtt_service_offline')
    host = state.get_global_setting('mqtt_host')
    self.mqtt_client.connect(host, port=1883)
    self.mqtt_client.loop_start()


  def run_end(self):
    alarm_controller.set_warn_alarm('mock_mqtt_service_offline', 'MockMQTT Service is Offline')
    self.mqtt_client.loop_stop()
    self.mqtt_client.disconnect()


  @profile_func(name='mock_mqtt_loop')
  def run_loop(self):
    packet = {
      'soil': [
        random.randint(300, 900),
        random.randint(300, 900),
        random.randint(300, 900),
        random.randint(300, 900)
      ],
      'dsb_temp': [
        random.randint(20, 40),
        random.randint(20, 40),
      ],
      'dht11_temp': [
        random.randint(20, 40),
        random.randint(20, 40),
      ],
      'dht11_humid': [
        random.randint(10, 80),
        random.randint(10, 80),
      ],
      'bmp_temp': [
        random.randint(20, 40),
        random.randint(20, 40),
      ],
      'bmp_pressure': [
        random.randint(100, 1000),
        random.randint(100, 1000),
      ],
    }

    self.mqtt_client.publish('board/mock_client/tx', json.dumps(packet))