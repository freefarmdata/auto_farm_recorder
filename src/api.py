from flask import Flask, redirect, render_template, request, jsonify, send_from_directory

import state

app = Flask(__name__)

def start():
  app.run(host='0.0.0.0', port=5000)

@app.route('/api/status', methods=['GET'])
def status():
  return jsonify(state.get_services_status()), 200

@app.route('/', methods=['GET'])
def index():
  return render_template('index.html')


