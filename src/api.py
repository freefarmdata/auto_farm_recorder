from flask import Flask, request, jsonify

app = Flask(__name__)

def start():
  app.run(host='0.0.0.0', port=5000)

@app.route('/api/soil/<int:start>/<int:end>', methods=['GET'])
def soil_data():
  return jsonify([]), 200

