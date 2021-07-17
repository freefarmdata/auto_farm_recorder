from threading import Thread
import logging
import os

from flask import Flask, render_template, send_from_directory, request
from flask_cors import CORS

from util.no_cache import no_cache

app = Flask(__name__)
cors = CORS(app, resources={r"/*":{"origins":"*"}})

logger = logging.getLogger()

class API(Thread):

    def __init__(self, config):
        super().__init__(daemon=True)
        self.config = config

    def run(self):
        app.config['CONFIG'] = self.config
        app.run(
            host='0.0.0.0',
            port=5454,
            debug=False,
            threaded=True
        )


@app.route('/streams', methods=['GET'])
def streams():
    config = app.config['CONFIG']
    return config.get('streams'), 200


@app.route('/stream/<string:file_name>', methods=['GET'])
@no_cache
def stream(file_name):
    config = app.config['CONFIG']
    stream_dir = os.path.abspath(config.get('stream_dir'))
    return send_from_directory(directory=stream_dir, filename=file_name)


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')
