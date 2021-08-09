import os
import logging
import pickle
from datetime import datetime, timedelta

from fservice import state
import numpy
import pandas
from tensorflow import keras
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

from util.time_util import profile_func

import database


logger = logging.getLogger()


def get_model_files():
    """
    Returns a list of all the soil models sorted by the timestamp
    of the model. Looks for models in the format of: `soil_name.h5`
    """
    model_dir = state.get_global_setting('model_dir')
    model_files = [os.path.join(model_dir, f) for f in os.listdir(model_dir)]
    model_files = list(filter(lambda f: f.startswith('soil'), model_files))
    return model_files


def load_best_model():
    '''
    Loads the active or lasted model that was trained
    '''
    active = database.get_active_model()
    if len(active) > 0:
        logger.info(f"Loading active model '{active[0]['name']}'")
        return load_model_by_name(active[0]['name'])

    models = database.query_for_models()
    if len(models) > 0:
        models = sorted(models, key=lambda f: f['end_time'].timestamp())
        return load_model_by_name(models[0]['name'])


def load_model_by_name(name):
    model_dir = state.get_global_setting('model_dir')
    model_path = os.path.join(model_dir, f'soil_{name}.h5')
    scaler_path = os.path.join(model_dir, f'sscaler_{name}.pickle')
    model, scaler = None
    if os.path.exists(model_path) and os.path.exists(scaler_path):
        model = keras.models.load_model(model_path)
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        return model, scaler


def get_blank_model():
    model = keras.models.Sequential([
        keras.layers.Dense(
            units=32,
            activation='relu'
        ),
        keras.layers.Dropout(0.3),
        keras.layers.Dense(
            units=1,
            activation='relu'
        ),
    ])
    model.compile(
        loss=keras.losses.MeanSquaredError(),
        optimizer=keras.optimizers.Adam(
            lr=0.001,
        ),
        metrics=['mse']
    )
    return model


@profile_func(name="train_new_model")
def train_new_model(data):
    model = get_blank_model()

    data = [[d['value'], int(d['timestamp']*1E3)] for d in data]
    df = pandas.DataFrame(data, columns=['value', 'timestamp'])

    df.timestamp = pandas.to_datetime(df.timestamp, unit='ms')

    df = df.groupby(pandas.Grouper(key='timestamp', freq='5min'))['value'].agg('median')
    df = df.to_frame().reset_index()
    df.timestamp = df.timestamp.astype(numpy.int64) / 1E6
    df = df.dropna()
    matrix = df.to_numpy()

    scaler = MinMaxScaler((0, 1)).fit(matrix)
    matrix = scaler.transform(matrix)

    x = matrix[:, 0].reshape(-1, 1)
    y = matrix[:, 1].reshape(-1, 1)

    x_train, x_test, y_train, y_test = train_test_split(x, y, random_state=42)

    model.fit(
        x=x_train,
        y=y_train,
        batch_size=50,
        epochs=30,
        verbose=0,
    )

    y_pred = model.predict(x_test)
    error = mean_squared_error(y_test, y_pred)

    return model, scaler, error


def predict_on_latest(model, scaler):
    # get the last 5 minutes of soil readings
    now = datetime.now()
    ago = now - timedelta(minutes=5)
    latest_soil = database.query_for_soil(ago, now)

    if len(latest_soil) <= 0:
        logger.error('No soil data to predict on in last five minutes')
        return

    # find the median value from those readings
    median_soil = numpy.median([s['value'] for s in latest_soil])

    # the first reading is what the soil moisture is currently at
    # the second reading is what the soil moisture should be at
    # when we want to water the plants again
    soil_threshold = state.get_service_setting('soil_predictor', 'threshold')
    matrix = [[median_soil], [soil_threshold]]

    # create a scaler from the old training scaler
    new_scaler = MinMaxScaler((0, 1))
    new_scaler.min_, new_scaler.scale_ = scaler.min_[0], scaler.scale_[0]

    # predict on both readings. This will give us the predicted
    # times for both the start and end
    y_pred = model.predict(matrix)

    # subtract the prediction of the soil now from when the
    # soil is predicted to be past the threshold.
    y_pred = new_scaler.inverse_transform(y_pred)
    time_left = y_pred[1][0] - y_pred[0][0]

    return time_left