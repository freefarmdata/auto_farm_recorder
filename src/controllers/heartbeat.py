

web_data = {
    'next_water_prediction': None,
    'latest_soil_reading': None,
    'latest_pressure_reading': None,
    'latest_light_reading': None,
}


def set_latest_light_reading(reading):
    global web_data
    web_data['latest_light_reading'] = reading


def set_latest_pressure_reading(reading):
    global web_data
    web_data['latest_pressure_reading'] = reading


def set_latest_soil_reading(reading):
    global web_data
    web_data['latest_soil_reading'] = reading


def set_next_water_prediction(prediction):
    global web_data
    web_data['next_water_prediction'] = prediction


def get_web_data():
    global web_data
    return web_data