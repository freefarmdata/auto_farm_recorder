from flask import Flask, redirect, render_template, request, jsonify, send_from_directory, Response
from flask_cors import CORS
from threading import Thread
import logging

app = Flask(__name__)
cors = CORS(app, resources={r"/*":{"origins":"http://localhost:3000"}})

logger = logging.getLogger(__name__)

class API(Thread):

    def __init__(self, config):
        super().__init__(daemon=True)
        self.config = config

    def run(self):
        app.config['CONFIG'] = self.config
        app.run(
            app,
            host='0.0.0.0',
            port=5001,
            debug=False
        )



@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')
