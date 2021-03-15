import os
import logging
from datetime import datetime, timedelta

import numpy
import pandas

from tensorflow import keras
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from sklearn.model_selection import train_test_split

import database
import state

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
        models = sorted(models, key=lambda f: f['end_time'])
        return load_model_by_name(models[0]['name'])


def load_model_by_name(name):
    model_dir = state.get_global_setting('model_dir')
    model_path = os.path.join(model_dir, f'soil_{name}')
    if os.path.exists(model_path):
        return keras.models.load_model(model_path)


def get_new_model():
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


def train_new_model(data):
    model = get_new_model()

    data = [[d['value'], d['timestamp']] for d in data]
    df = pandas.DataFrame(data, columns=['value', 'timestamp'])
    df.timestamp = pandas.to_datetime(df.timestamp, unit='ms')

    df = df.groupby(pd.Grouper(key='timestamp', freq='5min'))['value'].agg('median')
    df = df.to_frame().reset_index()
    df.timestamp = df.timestamp.astype(numpy.int64) / 1E6
    df = df.dropna()
    matrix = df.to_numpy()

    scaler = MinMaxScaler((0, 1)).fit(matrix)
    matrix = scaler.transform(matrix)

    x = matrix[:, 0].reshape(-1, 1)
    y = matrix[:, 1].reshape(-1, 1)

    x_train, x_val, y_train, y_val = train_test_split(x, y, random_state=42)

    history = model.fit(
        x=x_train,
        y=y_train,
        batch_size=50,
        epochs=30,
        validation_data=(x_val, y_val),
        verbose=0,
    )

    error = 1.23456

    return model, error


def predict_on_latest(model):
    now = datetime.datetime.now()
    ago = now - timedelta(minutes=5)
    
    latest_soil = database.query_for_soil(ago, now)

    median_soil = numpy.median([s['value'] for s in latest_soil])

    latest_reading = [median_soil, latest_soil[-1]['timestamp']]
    next_reading = [state.get_service_setting('soil_predictor', 'threshold'), 0]

    matrix = [latest_reading, next_reading]

    scaler = MinMaxScaler((0, 1)).fit()
    matrix = scaler.transform(matrix)

    x = matrix[:, 0].reshape(-1, 1)
    y = matrix[:, 1].reshape(-1, 1)

    y_pred = model.predict(x)

    # subtract the prediction of the soil now from when the
    # soil is predicted to be past the threshold
    time_left = y_pred[1][0] - y_pred[0][0]

    # inverse the transform to get milliseconds left before another watering
    time_left = scaler.inverse_transform([[0, time_left]])[0][-1]

    return time_left