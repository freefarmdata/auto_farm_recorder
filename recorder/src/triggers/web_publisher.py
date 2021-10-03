import logging
import json

import paho.mqtt.client as mqtt
from fservice import state
from fservice.trigger import Trigger

from util.time_util import profile_func

logger = logging.getLogger()

"""
MQTT_ERR_SUCCESS = 0
MQTT_ERR_NOMEM = 1
MQTT_ERR_PROTOCOL = 2
MQTT_ERR_INVAL = 3
MQTT_ERR_NO_CONN = 4
MQTT_ERR_CONN_REFUSED = 5
MQTT_ERR_NOT_FOUND = 6
MQTT_ERR_CONN_LOST = 7
MQTT_ERR_TLS = 8
MQTT_ERR_PAYLOAD_SIZE = 9
MQTT_ERR_NOT_SUPPORTED = 10
MQTT_ERR_AUTH = 11
MQTT_ERR_ACL_DENIED = 12
MQTT_ERR_UNKNOWN = 13
MQTT_ERR_ERRNO = 14
MQTT_ERR_QUEUE_SIZE = 15
"""

class WebPublisher(Trigger):
  """
  Trigger used to send a web socket messages to the
  web using mqtt
  """

  def __init__(self):
    super().__init__(name='web_publisher')
    self.set_block_time(1)
    self.mqtt_client = mqtt.Client(transport='websockets')


  def run_start(self):
    host = state.get_global_setting('mqtt_host')
    self.mqtt_client.connect_async(host, port=9001)
    self.mqtt_client.ws_set_options(path="/mqtt", headers=None)
    self.mqtt_client.loop_start()


  def run_trigger(self, message):
    self.mqtt_client.publish(message[0], json.dumps(message[1]))


  def run_end(self):
    self.mqtt_client.loop_stop()
    self.mqtt_client.disconnect()