import logging
import os

import controllers.watering as water_controller
import controllers.soil_predictor as soil_predictor
import controllers.program as program_controller

from util.service import Service
from util.time_util import min_to_nano, profile_func
import state
import database

logger = logging.getLogger(__name__)

class SoilPredictor(Service):


    def __init__(self):
        super().__init__()
        self.set_interval(min_to_nano(30))
        self.model = None


    def run_start(self):
        self.model = soil_predictor.get_latest_model()

    @profile_func(name='soil_predictor_update')
    def run_update(self, message):
        if message.get('action') == 'train':
            self.train_new_model(message.get('start_time'), message.get('end_time'))
            return

        if message.get('action') == 'select':
            self.select_model(message.get('name'))
            return

    @profile_func(name='soil_predictor_loop')
    def run_loop(self):
        if not self.model:
            logger.info('No model to test soil moisture with')
            return

        ms_time_left = soil_predictor.predict_on_latest()
        program_controller.set_next_water_prediction(ms_time_left)


    def select_model(self, name):
        pass


    def train_new_model(self, start_time, end_time):
        data = database.query_for_soil(start_time, end_time)
        new_model = soil_predictor.train_new_model(new_model)
        model_dir = state.get_global_setting('model_dir')
        model_name = f'soil_{start_time}_{end_time}'
        model_path = os.path.join(model_dir, model_name)
        new_model.save_model(model_path)
        self.model = new_model
