import logging
import datetime
import random
import os

from tensorflow import keras

import controllers.watering as water_controller
import controllers.soil_predictor as soil_predictor
import controllers.program as program_controller

from util.service import Service
from util.names import random_name
from util.time_util import min_to_nano, profile_func
import state
import database

logger = logging.getLogger(__name__)

class SoilPredictor(Service):


    def __init__(self):
        super().__init__()
        self.set_interval(min_to_nano(1))
        self.model = None


    def run_start(self):
        self.model = soil_predictor.load_best_model()


    @profile_func(name='soil_predictor_update')
    def run_update(self, message):
        if message is not None:
            if message.get('action') == 'train':
                self.train_new_model(message.get('start_time'), message.get('end_time'))
            elif message.get('action') == 'select':
                self.select_model(message.get('name'))
            elif message.get('action') == 'delete':
                self.delete_model(message.get('name'))
            elif message.get('action') == 'predict':
                self.predict_soil()


    @profile_func(name='soil_predictor_loop')
    def run_loop(self):
        self.predict_soil()

    
    def predict_soil(self):
        if not self.model:
            logger.info('No model to test soil moisture with')
            return
        ms_time_left = soil_predictor.predict_on_latest(self.model)
        if ms_time_left is not None:
            program_controller.set_info_key('next_water_prediction', ms_time_left)

    
    def delete_model(self, name):
        logger.info(f'Deleting soil model with name {name}')
        database.delete_model(name)
        model_dir = state.get_global_setting('model_dir')
        model_path = os.path.join(model_dir, f'soil_{name}.h5')
        if os.path.exists(model_path):
            os.remove(model_path)
        
        soil_models = database.query_for_models()
        program_controller.set_info_key('soil_models', soil_models)


    def select_model(self, name):
        logger.info(f'Selecting a soil model with name {name}')
        database.set_model_active(name)
        model = soil_predictor.load_model_by_name(name)
        self.model = model
        soil_models = database.query_for_models()
        program_controller.set_info_key('soil_models', soil_models)


    def train_new_model(self, start_time, end_time):
        # convert unix ms time to datetime python objects
        start_date = datetime.datetime.fromtimestamp(start_time)
        end_date = datetime.datetime.fromtimestamp(end_time)

        logger.info(f'Training new model from {start_date} to {end_date}')

        # query for soil moisture over the time span
        data = []
        if state.get_global_setting('devmode'):
            data = self.generate_random_soil_data(start_time, end_time)
        else:
            data = database.query_for_soil(start_date, end_date)

        # can't train on empty data
        if len(data) <= 0:
            logger.error('Training new model failed. No data to train on.')
            return

        # train the new model based on the soil data
        new_model, error = soil_predictor.train_new_model(data)

        # upsert the model in SQL and save it to disk
        model_dir = state.get_global_setting('model_dir')
        model_name = random_name()
        model_path = os.path.join(model_dir, f'soil_{model_name}.h5')
        database.insert_model(model_name, start_date, end_date, error)
        keras.models.save_model(new_model, model_path)
        self.model = new_model

        # update the program controller soil models
        soil_models = database.query_for_models()
        program_controller.set_info_key('soil_models', soil_models)

        logger.info(f"New model '{model_name}' trained with error: {error}")


    def generate_random_soil_data(self, start_time, end_time):
        number_of_readings = 10000
        start_soil = 200
        end_soil = 550

        t_to_add = (end_time - start_time) / number_of_readings
        s_to_add = (end_soil - start_soil) / number_of_readings

        data = []
        for _ in range(number_of_readings+1):
            start_soil += s_to_add
            start_time += t_to_add
            data.append({ 'value': start_soil, 'timestamp': start_time })
        
        return data
