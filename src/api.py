from flask import Flask, redirect, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import logging

import state

import controllers.watering as watering_controller
import controllers.image as image_controller
import controllers.program as program_controller

app = Flask(__name__)
cors = CORS(app, resources={r"/*":{"origins":"http://localhost:3001"}})
socketio = SocketIO(app, cors_allowed_origins='http://localhost:3001')

logger = logging.getLogger(__name__)


def start():
    logger.info('Starting API')
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)


@socketio.on('data', namespace='/')
def fetch_data(message):
    emit('data', program_controller.get_web_data(), broadcast=True)


@socketio.on('latest_image', namespace='/')
def latest_image(message):
    latest_image = image_controller.get_latest_image()
    if message.get('time') != latest_image['time']:
        emit('latest_image', latest_image, broadcast=True)


@socketio.on('toggle_water', namespace='/')
def toggle_water(message):
    logger.info(f'toggle water {message}')
    if message['state']:
        watering_controller.set_water_time()
    else:
        watering_controller.clear_water_time()


@socketio.on('select_model', namespace='/')
def select_model(message):
    logger.info(f'select model {message}')
    state.update_service('soil_predictor', {
        'action': 'select',
        'name': message['name'],
    })


@socketio.on('predict_model', namespace='/')
def predict_model(message):
    logger.info(f'predict model')
    state.update_service('soil_predictor', { 'action': 'predict' })


@socketio.on('delete_model', namespace='/')
def delete_model(message):
    logger.info(f'delete model {message}')
    state.update_service('soil_predictor', {
        'action': 'delete',
        'name': message['name']
    })


@socketio.on('train_model', namespace='/')
def select_model(message):
    logger.info(f'train model {message}')
    state.update_service('soil_predictor', {
        'action': 'train',
        'start_time': message['startTime'],
        'end_time': message['endTime']
    })


@socketio.on('toggle_service', namespace='/')
def toggle_service(message):
    logger.info(f'toggle service {message}')
    if message['state']:
        state.start_service(message['service'])
    else:
        state.stop_service(message['service'])


@socketio.on('restart_service', namespace='/')
def restart_service(message):
    logger.info(f'restart service {message}')
    state.stop_service(message['service'])
    state.start_service(message['service'])


@app.route('/api/restart/<service_name>', methods=['GET'])
def reset_service(service_name):
    state.stop_service(service_name)
    state.start_service(service_name)
    return 'OK', 200


@app.route('/api/status', methods=['GET'])
def status():
    return jsonify(state.get_services_status()), 200


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')
