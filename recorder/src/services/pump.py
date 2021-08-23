import logging
import json

import requests
from fservice import state
from fservice.tservice import TService

from util.time_util import profile_func
import database

logger = logging.getLogger()

class Pump(TService):


    def __init__(self):
        super().__init__()
        self.set_interval(5e9)


    def run_start(self):        
        pass


    @profile_func(name='pump_loop')
    def run_loop(self):
        message = self.read_pump_board()
        self.save_sensor_data(message)


    @profile_func(name='pump_update')
    def run_update(self, message):
        if message is not None:
            if message.get('action') == 'activate':
                self.activate_pump(message.get('parameters'))
            if message.get('action') == 'deactivate':
                self.deactivate_pump()


    def run_end(self):
        pass


    def deactivate_pump(self):
        try:
            host_url = state.get_service_setting('pump', 'host_url')
            requests.put(f'{host_url}/deactivate', timeout=(5, 5))
        except:
            logger.exception('Failed to deactivate pump')


    def activate_pump(self, parameters):
        try:
            data = json.dump(parameters)
            host_url = state.get_service_setting('pump', 'host_url')
            requests.put(f'{host_url}/activate', data=data, timeout=(5, 5))
        except:
            logger.exception('Failed to activate pump')


    def read_pump_board(self):
        try:
            host_url = state.get_service_setting('pump', 'host_url')
            response = requests.get(f'{host_url}/telemetry', timeout=(5, 5))
            return json.loads(response.text)
        except:
            logger.exception('Failed to read pump data')


    def save_sensor_data(self, message):
        metrics = {'level': []}
        for metric in message:
            if metric in metrics:
                for i,v in enumerate(message[metric]):
                    metrics[metric].append({'sensor': i, 'value': v, 'board_id': message['id']})

        for metric in metrics:
            database.insert_timeseries(metric, metrics[metric])
