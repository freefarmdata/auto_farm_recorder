from flask import Flask, redirect, render_template, request, jsonify, send_from_directory
import base64
import cv2

import state

latest_image = None
app = Flask(__name__)

def start():
  app.run(host='0.0.0.0', port=5000)


@app.route('/api/status', methods=['GET'])
def status():
  return jsonify(state.get_services_status()), 200


def set_latest_image(image):
  global latest_image
  _, buffer = cv2.imencode('.png', image)
  latest_image = str(base64.b64encode(buffer), 'utf-8')


@app.route('/api/latest_image', methods=['GET'])
def image():
  return latest_image, 200


@app.route('/', methods=['GET'])
def index():
  return render_template('index.html')
  



