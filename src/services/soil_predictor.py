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
        self.set_interval(min_to_nano(10))
        self.model = None


    def run_start(self):
        self.model = soil_predictor.load_best_model()


    @profile_func(name='soil_predictor_update')
    def run_update(self, message):
        if message is not None:
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
        program_controller.set_info_key('next_water_prediction', ms_time_left)


    def select_model(self, name):
        logger.info(f'Selecting a soil model with name {name}')
        database.set_model_active(name)
        model = soil_predictor.load_model_by_name(name)
        self.model = model
        soil_models = database.query_for_models()
        program_controller.set_info_key('soil_models', soil_models)


    def train_new_model(self, start_time, end_time):
        data = database.query_for_soil(start_time, end_time)
        new_model, error = soil_predictor.train_new_model(data)
        model_name = str('new model name')
        database.insert_model(model_name, start_time, end_time, error)
        model_dir = state.get_global_setting('model_dir')
        model_path = os.path.join(model_dir, f'soil_{model_name}')
        new_model.save_model(model_path)
        self.model = new_model
        soil_models = database.query_for_models()
        program_controller.set_info_key('soil_models', soil_models)
