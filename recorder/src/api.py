from threading import Thread
import logging
import os

from fservice import state
from flask import Flask, json, request, send_file, jsonify, send_from_directory
from flask_cors import CORS

from util.no_cache import no_cache

import database
import controllers.alarms as alarm_controller
import controllers.settings as settings_controller

app = Flask(__name__)
cors = CORS(app, resources={r"/*":{"origins":"*"}})

logger = logging.getLogger()

class API(Thread):

    def __init__(self):
        super().__init__(daemon=True)

    def run(self):
        app.run(
            host='0.0.0.0',
            port=5000,
            threaded=True,
            debug=False
        )


@app.route('/api/update-service', methods=['POST'])
def update_service(message):
    message = request.get_json(force=True)
    logger.info(f'update service {message}')
    state.update_service(message['service_name'], message['message'])
    return 'OK', 200 


@app.route('/api/update-setting', methods=['POST'])
def update_setting():
    message = request.get_json(force=True)
    logger.info(f'update setting {message}')
    if message['service_name'] == 'global':
        state.set_global_setting(message['key'], message['value'])
    else:
        state.set_service_setting(message['service_name'], message['key'], message['value'])
    return 'OK', 200


@app.route('/api/update-settings', methods=['POST'])
def update_settings():
    message = request.get_json(force=True)
    logger.info(f'update settings {message}')
    for service_name in message:
        if service_name == 'global':
            for key in message[service_name]:
                state.set_global_setting(key, message[service_name][key])
        else:
            for key in message[service_name]:
                state.set_service_setting(service_name, key, message[service_name][key])
    settings_controller.save_settings(message)
    return 'OK', 200


@app.route('/api/settings', methods=['GET'])
def get_settings():
    settings = state.get_all_settings()
    return jsonify(settings), 200


@app.route('/api/activate-service/<service_name>', methods=['GET'])
def toggle_on_service(service_name):
    logger.info(f'toggling service {service_name} on')
    state.start_service(service_name)
    return 'OK', 200


@app.route('/api/deactivate-service/<service_name>', methods=['GET'])
def toggle_off_service(service_name):
    logger.info(f'toggling service {service_name} off')
    state.stop_service(service_name)
    return 'OK', 200


@app.route('/api/disable-service/<service_name>', methods=['GET'])
def disable_service(service_name):
    logger.info(f'disabling service {service_name}')
    state.set_service_setting(service_name, 'disabled', True)
    state.stop_service(service_name)
    return 'OK', 200


@app.route('/api/enable-service/<service_name>', methods=['GET'])
def enable_service(service_name):
    logger.info(f'disabling service {service_name}')
    state.set_service_setting(service_name, 'disabled', False)
    return 'OK', 200


@app.route('/api/last-points', methods=['GET'])
def last_points():
    boards = request.args.get('boards').split(',')
    amount = request.args.get('amount')
    logger.info(f'last data {amount} points for: {boards}')

    results = []
    for board in boards:
        data = database.query_latest_data(board=board, amount=amount)
        results.extend(data)

    return jsonify(results), 200


@app.route('/api/streams', methods=['GET'])
def streams():
    return state.get_service_setting('streamer', 'streams'), 200


@app.route('/api/stream/<string:file_name>', methods=['GET'])
@no_cache
def stream(file_name):
    stream_dir = os.path.abspath(state.get_global_setting('stream_dir'))
    return send_from_directory(directory=stream_dir, filename=file_name)


@app.route('/api/status', methods=['GET'])
def status():
    return jsonify(state.get_services_status()), 200


@app.route('/api/database/watering-times', methods=['GET'])
def watering_times():
    return jsonify(database.query_for_watering()), 200


@app.route('/api/active-alarms', methods=['GET'])
def get_active_alarms():
    return jsonify(alarm_controller.get_active_alarms()), 200


@app.route('/api/clear-alarm/<alarm_id>', methods=['GET'])
def clear_alarm(alarm_id):
    alarm_controller.clear_alarm(alarm_id)
    return 'OK', 200


@app.route('/health', methods=['GET'])
def health():
    return 'OK', 200
