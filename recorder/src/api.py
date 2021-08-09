from threading import Thread
import logging

from fservice import state
from flask import Flask, redirect, render_template, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from flask_socketio import SocketIO, emit

import database
import controllers.watering as watering_controller
import controllers.image as image_controller
import controllers.program as program_controller

app = Flask(__name__)
cors = CORS(app, resources={r"/*":{"origins":"http://localhost:3000"}})
socketio = SocketIO(app,
    cors_allowed_origins='http://localhost:3000',
    async_mode='threading',
)

logger = logging.getLogger(__name__)

class API(Thread):

    def __init__(self):
        super().__init__(daemon=True)

    def run(self):
        socketio.run(
            app,
            host='0.0.0.0',
            port=5000,
            debug=False
        )


@socketio.on('data', namespace='/')
def fetch_data(message):
    emit('data', program_controller.get_web_data(), broadcast=True)


@socketio.on('update_service', namespace='/')
def update_service(message):
    logger.info(f'update service {message}')
    state.update_service(message['service_name'], message['message'])


@socketio.on('update_setting', namespace='/')
def update_setting(message):
    logger.info(f'update setting {message}')
    if message['service_name'] == 'global':
        state.set_global_setting(message['key'], message['value'])
    else:
        state.set_service_setting(message['service_name'], message['key'], message['value'])


@socketio.on('toggle_service', namespace='/')
def toggle_service(message):
    logger.info(f'toggle service {message}')
    if message['state']:
        state.start_service(message['service'])
    else:
        state.stop_service(message['service'])


@socketio.on('disable_service', namespace='/')
def disable_service(message):
    logger.info(f'disable service {message}')
    if state.get_service_setting(message['service_name'], 'disabled'):
        state.set_service_setting(message['service_name'], 'disabled', False)
    else:
        state.set_service_setting(message['service_name'], 'disabled', True)
        state.stop_service(message['service_name'])


@app.route('/api/status', methods=['GET'])
def status():
    return jsonify(state.get_services_status()), 200


@app.route('/api/watering-times', methods=['GET'])
def watering_times():
    return jsonify(database.query_for_watering()), 200


@app.route('/api/active-alarms', methods=['GET'])
def active_alarms():
    import controllers.alarms as alarm_controller
    return jsonify(alarm_controller.get_active_alarms()), 200


@app.route('/api/clear-alarm/<alarm_id>', methods=['GET'])
def clear_alarm(alarm_id):
    import controllers.alarms as alarm_controller
    alarm_controller.clear_alarm(alarm_id)
    return 'OK', 200


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')
