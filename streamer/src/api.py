from threading import Thread
import logging
import os

from flask import Flask, render_template, send_from_directory
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/*":{"origins":"*"}})

logger = logging.getLogger(__name__)

class API(Thread):

    def __init__(self, config):
        super().__init__(daemon=True)
        self.config = config

    def run(self):
        app.config['CONFIG'] = self.config
        app.run(
            host='0.0.0.0',
            port=5454,
            debug=False
        )

@app.route('/streams', methods=['GET'])
def streams():
    config = app.config['CONFIG']
    return config.get('streams'), 200


@app.route('/stream/<string:file_name>', methods=['GET'])
def stream(file_name):
    config = app.config['CONFIG']
    video_dir = os.path.abspath(config.get('video_dir'))
    return send_from_directory(directory=video_dir, filename=file_name)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')
