import datetime
import logging
import json

from fservice import state
from fservice.tservice import TService
import paho.mqtt.client as mqtt

from util.time_util import profile_func
import controllers.alarms as alarm_controller
import database

logger = logging.getLogger()

class MQTTBoard(TService):


  def __init__(self):
    super().__init__(name="mqtt_board")
    self.set_interval(30E9)
    self.mqtt_client = mqtt.Client()


  def run_start(self):
    alarm_controller.clear_alarm('mqtt_board_service_offline')
    host = state.get_global_setting('mqtt_host')
    self.mqtt_client.connect(host, port=1883)
    self.mqtt_client.loop_start()
    self.subscribe_to_boards()


  def run_end(self):
    alarm_controller.set_warn_alarm('mqtt_board_service_offline', 'MQTTBoard Service Is Offline')
    self.mqtt_client.loop_stop()
    self.mqtt_client.disconnect()


  def subscribe_to_boards(self):
    boards = state.get_service_setting('mqtt_board', 'boards')
    if boards is not None:
      for board in boards:
        self.mqtt_client.subscribe(f'board/{board}/tx')
    self.mqtt_client.on_message = self.on_message()


  def on_message(self):
    def on_mqtt_message(_, userdata, message):
      if message.topic.endswith('tx'):
        self.on_tx_message(message)

    return on_mqtt_message
  
  def on_tx_message(self, message):
    board_id = message.topic.split('/')[1]

    metrics = [
      'soil',
      'dsb',
      'dht11_temp',
      'dht11_humid',
      'bmp_temp',
      'bmp_pressue',
      'light'
    ]

    readings = []
  
    packet = message.payload.decode()
    packet = json.loads(packet)
    timestamp = datetime.datetime.now()

    for metric in metrics:
      if metric in packet:
        for i,v in enumerate(packet[metric]):
          reading = {
            'timestamp': timestamp,
            'board': board_id,
            'metric': metric,
            'sensor': i,
            'value': v,
          }
          readings.append(reading)
          state.update_trigger('web_publisher', (
            f"web/board/{reading.get('board')}/{reading.get('metric')}",
            { **reading, 'timestamp': reading['timestamp'].timestamp() }
          ))

    database.insert_readings(readings)

