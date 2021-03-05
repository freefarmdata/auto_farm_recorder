from flask import Flask, redirect, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit

import state

import controllers.watering as watering_controller
import controllers.image as image_controller
import controllers.heartbeat as heart_controller

app = Flask(__name__)
socketio = SocketIO(app)


def start():
    socketio.run(app)


@socketio.on('data')
def fetch_data():
    emit('data', heart_controller.get_web_data())


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
