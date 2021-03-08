from flask import Flask, redirect, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import logging

import state

import controllers.watering as watering_controller
import controllers.image as image_controller
import controllers.program as program_controller

app = Flask(__name__)
cors = CORS(app, resources={r"/*":{"origins":"http://localhost:3000"}})
socketio = SocketIO(app, cors_allowed_origins='http://localhost:3000')

logger = logging.getLogger(__name__)


def start():
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)


@socketio.on('data', namespace='/')
def fetch_data(message):
    emit('data', program_controller.get_web_data(), broadcast=True)


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



@app.route('/api/reset/<service_name>', methods=['GET'])
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


@app.route('/api/get/latest_image', methods=['GET'])
def get_latest_image():
    return image_controller.get_latest_image()


@app.route('/api/get/water', methods=['GET'])
def get_water_time():
    return watering_controller.get_water_time()


@app.route('/api/set/water', methods=['GET'])
def set_water_time():
    return watering_controller.set_water_time()


@app.route('/api/clear/water', methods=['GET'])
def clear_water_time():
    watering_controller.clear_water_time()
